# Research: Universal Front Door Support Agent

**Date**: 2026-01-20
**Feature**: 1-front-door-agent

## Overview

This document captures technical research and decisions for the Front Door Support Agent implementation. All "NEEDS CLARIFICATION" items from the technical context have been resolved through user clarification sessions or best-practice analysis.

---

## 1. LLM Service Selection

### Decision
Azure OpenAI GPT-4o for intent classification and entity extraction.

### Rationale
- Azure OpenAI is available in Azure AI Foundry with enterprise SLAs
- GPT-4o provides excellent few-shot classification performance for 30+ intent categories
- Native Azure integration simplifies authentication and compliance
- Supports structured output (JSON mode) for reliable parsing of intents/entities

### Alternatives Considered
| Option | Pros | Cons | Rejected Because |
|--------|------|------|------------------|
| Azure Claude (Anthropic) | Excellent reasoning | Limited availability in Azure AI Foundry as of Jan 2026 | Deployment complexity; GPT-4o sufficient |
| Fine-tuned BERT | Lower latency, no per-token cost | Requires labeled training data, harder to add new intents | Clarification confirmed LLM approach preferred |
| Hybrid keyword + LLM | Lower cost for common intents | Maintenance burden, inconsistent behavior | Added complexity without significant benefit |

---

## 2. Three-Agent Architecture Pattern

### Decision
Implement QueryAgent, RouterAgent, and ActionAgent as separate Python classes with distinct interfaces and no cross-boundary method access.

### Rationale
- Constitution Principle I (Bounded Agent Authority) mandates architectural separation
- Each agent has a single responsibility:
  - **QueryAgent**: Analyzes query → returns `QueryResult` (intent, entities, confidence, PII flag, sentiment)
  - **RouterAgent**: Takes `QueryResult` → returns `RoutingDecision` (department, priority, escalation)
  - **ActionAgent**: Takes `RoutingDecision` → returns `ActionResult` (ticket, KB articles, response)
- Boundaries enforced by interface design: ActionAgent has no `approve_refund()` method because it doesn't exist

### Implementation Pattern
```python
# Each agent receives only the services it needs
class QueryAgent:
    def __init__(self, llm_service: LLMService, pii_detector: PIIDetector):
        # NO ticket_service, NO session_service

class RouterAgent:
    def __init__(self, routing_config: RoutingConfig):
        # NO llm_service, NO ticket_service

class ActionAgent:
    def __init__(self, ticket_service: TicketService, knowledge_service: KnowledgeService):
        # NO approve_service (doesn't exist)
```

---

## 3. Session Storage

### Decision
Azure Cosmos DB with 90-day TTL for session documents.

### Rationale
- Native TTL support for automatic 90-day expiration (per NFR-004)
- Scales to 500 concurrent users without configuration
- JSON document model fits session structure naturally
- Global distribution available for future multi-region deployment

### Alternatives Considered
| Option | Pros | Cons | Rejected Because |
|--------|------|------|------------------|
| Azure Redis Cache | Sub-ms latency | No native TTL beyond 24h, persistence complexity | Session retention requires 90 days |
| Azure SQL | Familiar relational model | Schema rigidity for evolving session structure | Document model better fits conversation history |
| Azure Table Storage | Low cost | Limited query capabilities | Need to query by student_id efficiently |

### Schema Design
```json
{
  "id": "session_abc123",
  "partition_key": "student_hash_xyz",
  "student_id_hash": "sha256_of_student_id",
  "created_at": "2026-01-20T10:30:00Z",
  "last_active": "2026-01-20T10:45:00Z",
  "conversation_history": [
    {"turn": 1, "intent": "password_reset", "ticket_id": "TKT-IT-20260120-0001"}
  ],
  "ttl": 7776000  // 90 days in seconds
}
```

---

## 4. Knowledge Base Search

### Decision
Azure AI Search with semantic ranking over university help articles.

### Rationale
- Semantic search provides relevance beyond keyword matching
- Vector embeddings capture meaning ("can't log in" matches "password reset" articles)
- Relevance scores (0.0-1.0) can be displayed to users per FR-017
- Native Azure integration with Cosmos DB for hybrid scenarios

### Index Configuration
- **Fields**: title, content, department, url, last_updated
- **Semantic config**: Enabled on title + content
- **Scoring profile**: Boost recent articles, department-matched articles

---

## 5. Ticketing System Integration

### Decision
ServiceNow REST API with abstraction layer supporting mock mode.

### Rationale
- ServiceNow is the assumed ticketing system per spec assumptions
- Abstraction layer (interface + implementations) enables:
  - Mock implementation for demo/testing (returns synthetic tickets)
  - Production implementation for real ServiceNow API
- Ticket ID format: `TKT-{DEPT}-{YYYYMMDD}-{SEQ}` (per clarification)

### Interface Design
```python
class TicketService(Protocol):
    async def create_ticket(self, request: TicketRequest) -> Ticket: ...
    async def get_ticket_status(self, ticket_id: str) -> TicketStatus: ...

class MockTicketService(TicketService):
    # Returns synthetic tickets from mock_data/sample_tickets.json

class ServiceNowTicketService(TicketService):
    # Calls ServiceNow REST API
```

### ServiceNow API Details
- **Authentication**: OAuth 2.0 client credentials flow
- **Endpoint**: `POST /api/now/table/incident` for ticket creation
- **Rate limits**: 500 requests/minute (configurable per instance)

---

## 6. PII Detection Strategy

### Decision
Regex-based detection for known PII patterns + LLM-assisted detection for contextual PII.

### Rationale
- Regex catches structured PII: SSN (XXX-XX-XXXX), credit card numbers, phone numbers
- LLM catches contextual PII: "my student ID is 12345678" or embedded addresses
- Detection runs BEFORE any logging to ensure privacy-first handling
- Flagged queries have raw text excluded from audit logs

### Implementation
```python
class PIIDetector:
    def detect(self, text: str) -> PIIDetectionResult:
        # 1. Regex patterns for structured PII
        # 2. LLM prompt for contextual PII (if enabled)
        # Returns: has_pii (bool), pii_types (list), safe_text (redacted)
```

---

## 7. Frontend Architecture

### Decision
React 18 + TypeScript + Tailwind CSS with Claude.ai-inspired design.

### Rationale
- React provides component model for chat UI (messages, typing indicators, cards)
- TypeScript ensures type safety with backend API contracts
- Tailwind enables rapid styling with high-contrast mode via CSS variables
- Vite for fast development builds

### Accessibility Implementation
- High-contrast mode: Toggle switches CSS variables for WCAG AAA colors
- Keyboard navigation: All interactive elements focusable, Enter/Space to activate
- Screen reader: ARIA labels on all components, live regions for new messages
- Mobile: Responsive breakpoints, touch-friendly tap targets (44px minimum)

---

## 8. Authentication Flow

### Decision
University SSO via OAuth 2.0 / OpenID Connect with fallback to read-only mode.

### Rationale
- SSO assumption in spec means we don't build auth ourselves
- Backend validates JWT tokens from SSO provider
- Student ID extracted from token claims, then hashed for storage
- Per clarification: If SSO unavailable, allow read-only KB browsing

### Flow
1. Frontend redirects to university SSO login
2. SSO returns JWT token to frontend
3. Frontend includes token in `Authorization: Bearer {token}` header
4. Backend validates token, extracts student_id
5. If validation fails: Return 401, frontend shows KB-only mode

---

## 9. Escalation Logic

### Decision
RouterAgent implements all 6 escalation triggers as explicit boolean checks.

### Rationale
- Constitution Principle II requires deterministic escalation
- Each trigger is a separate, testable condition
- Escalation reason captured in `RoutingDecision.escalation_reason`

### Trigger Implementation
```python
def should_escalate(self, query_result: QueryResult, session: Session) -> tuple[bool, str]:
    if query_result.confidence < 0.70:
        return True, "confidence_too_low"
    if self._has_policy_keyword(query_result.entities):
        return True, "policy_keyword_detected"
    if self._has_sensitive_topic(query_result.intent):
        return True, "sensitive_topic"
    if self._needs_multi_department(query_result):
        return True, "multi_department_coordination"
    if query_result.intent == "request_human":
        return True, "user_requested_human"
    if session.clarification_attempts >= 3:
        return True, "max_clarifications_exceeded"
    return False, ""
```

---

## 10. Graceful Degradation Strategy

### Decision
Circuit breaker pattern with fallback implementations for each external service.

### Rationale
- Constitution Principle VII requires system to provide value during outages
- Circuit breakers prevent cascade failures
- Each service has a defined fallback behavior

### Fallback Matrix
| Service | Fallback Behavior |
|---------|-------------------|
| LLM (Azure OpenAI) | Keyword-based intent matching + escalate to human |
| Ticketing (ServiceNow) | Log request for retry, inform user, provide KB articles |
| Knowledge (AI Search) | Return empty results with "KB temporarily unavailable" message |
| Session (Cosmos DB) | Continue stateless, warn user context may be lost |

---

## Resolved Clarifications

All technical decisions have been resolved. No remaining "NEEDS CLARIFICATION" items.

| Item | Resolution | Source |
|------|------------|--------|
| Concurrent users | 500 | User clarification |
| SSO failure handling | Read-only KB access | User clarification |
| Intent classification | LLM with few-shot | User clarification |
| Mock mode | Dual-mode with abstractions | User clarification |
| Ticket ID format | TKT-{DEPT}-{YYYYMMDD}-{SEQ} | User clarification |
