# Data Model: Universal Front Door Support Agent

**Date**: 2026-01-20
**Feature**: 1-front-door-agent

## Overview

This document defines the data entities, their attributes, relationships, validation rules, and state transitions for the Front Door Support Agent system.

---

## Entities

### 1. Session

Represents a student's conversation context for multi-turn interactions.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | string (UUID) | Yes | Unique identifier for the session |
| `student_id_hash` | string (SHA-256) | Yes | Hashed student ID for privacy (never store raw) |
| `created_at` | datetime (ISO 8601) | Yes | Session creation timestamp |
| `last_active` | datetime (ISO 8601) | Yes | Last interaction timestamp |
| `conversation_history` | array[ConversationTurn] | Yes | List of conversation turns |
| `clarification_attempts` | integer | Yes | Count of disambiguation attempts (max 3) |
| `ttl` | integer | Yes | Time-to-live in seconds (7,776,000 = 90 days) |

**Nested: ConversationTurn**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `turn_number` | integer | Yes | Sequential turn number |
| `timestamp` | datetime | Yes | When this turn occurred |
| `intent` | string | Yes | Detected intent for this turn |
| `ticket_id` | string | No | Ticket created in this turn (if any) |
| `escalated` | boolean | Yes | Whether this turn resulted in escalation |

**Validation Rules**:
- `student_id_hash` must be exactly 64 characters (SHA-256 hex)
- `clarification_attempts` must be 0-3 (escalate at 3)
- `conversation_history` limited to 50 turns (older turns archived)

**Partition Key**: `student_id_hash` (enables efficient lookup by student)

---

### 2. AuditLog

Immutable record of each interaction for compliance and analytics.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `log_id` | string (UUID) | Yes | Unique identifier for this log entry |
| `timestamp` | datetime (ISO 8601) | Yes | When the interaction occurred |
| `student_id_hash` | string (SHA-256) | Yes | Hashed student ID |
| `session_id` | string (UUID) | Yes | Reference to parent session |
| `detected_intent` | string | Yes | Intent classification result |
| `confidence_score` | float (0.0-1.0) | Yes | Classification confidence |
| `routed_department` | Department | Yes | Where request was routed |
| `ticket_id` | string | No | Created ticket ID (if any) |
| `escalated` | boolean | Yes | Whether escalation occurred |
| `escalation_reason` | string | No | Reason for escalation (if escalated) |
| `pii_detected` | boolean | Yes | Whether PII was detected in query |
| `sentiment` | Sentiment | Yes | Detected sentiment |
| `response_time_ms` | integer | Yes | End-to-end response time |

**Validation Rules**:
- `confidence_score` must be between 0.0 and 1.0
- `escalation_reason` required if `escalated` is true
- Logs are append-only (no updates or deletes)
- Retention: 7 years minimum (FERPA compliance)

**Note**: Raw query text is NOT stored in audit logs to protect PII.

---

### 3. QueryResult

Output of the QueryAgent's intent detection and entity extraction.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `intent` | string | Yes | Primary detected intent |
| `intent_category` | IntentCategory | Yes | Category grouping |
| `department_suggestion` | Department | Yes | Suggested target department |
| `entities` | dict[string, any] | Yes | Extracted entities |
| `confidence` | float (0.0-1.0) | Yes | Classification confidence |
| `requires_escalation` | boolean | Yes | Pre-routing escalation flag |
| `pii_detected` | boolean | Yes | Whether PII was found |
| `pii_types` | array[string] | No | Types of PII detected |
| `sentiment` | Sentiment | Yes | Detected sentiment |
| `urgency_indicators` | array[string] | No | Urgency signals found |

**Entity Examples**:
```json
{
  "building": "Smith Hall",
  "course_code": "CS101",
  "date": "2026-01-20",
  "urgency": "tonight"
}
```

---

### 4. RoutingDecision

Output of the RouterAgent's routing logic.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `department` | Department | Yes | Target department for routing |
| `priority` | Priority | Yes | Request priority level |
| `escalate_to_human` | boolean | Yes | Whether human review required |
| `escalation_reason` | EscalationReason | No | Reason for escalation |
| `suggested_sla_hours` | integer | Yes | Expected response time in hours |
| `routing_rules_applied` | array[string] | Yes | Which rules determined this decision |

**Validation Rules**:
- `escalation_reason` required if `escalate_to_human` is true
- `suggested_sla_hours` must be positive integer

---

### 5. ActionResult

Output of the ActionAgent's execution.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ticket_id` | string | No | Created ticket ID (format: TKT-{DEPT}-{YYYYMMDD}-{SEQ}) |
| `ticket_url` | string (URL) | No | Link to ticket in ticketing system |
| `department` | Department | Yes | Department that received the request |
| `status` | ActionStatus | Yes | Outcome status |
| `knowledge_articles` | array[KnowledgeArticle] | Yes | Retrieved KB articles (max 3) |
| `estimated_response_time` | string | Yes | Human-readable SLA ("2 hours", "next business day") |
| `escalated` | boolean | Yes | Whether escalation occurred |
| `user_message` | string | Yes | Friendly response to display to student |

**Validation Rules**:
- `ticket_id` must match pattern `TKT-[A-Z]{2,3}-\d{8}-\d{4}`
- `knowledge_articles` limited to 3 items

---

### 6. KnowledgeArticle

Represents a help article from the knowledge base.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `article_id` | string | Yes | Unique article identifier |
| `title` | string | Yes | Article title |
| `url` | string (URL) | Yes | Link to full article |
| `snippet` | string | No | Brief preview (max 200 chars) |
| `relevance_score` | float (0.0-1.0) | Yes | Search relevance score |
| `department` | Department | No | Owning department |
| `last_updated` | datetime | No | When article was last modified |

---

## Enumerations

### Department
```
IT
HR
REGISTRAR
FINANCIAL_AID
FACILITIES
STUDENT_AFFAIRS
CAMPUS_SAFETY
ESCALATE_TO_HUMAN
```

### Priority
```
LOW        # Standard request, no urgency
MEDIUM     # Normal priority
HIGH       # Urgency indicators or frustrated sentiment
URGENT     # Sensitive topics, safety concerns
```

### Sentiment
```
NEUTRAL
FRUSTRATED
URGENT
SATISFIED
```

### ActionStatus
```
CREATED           # Ticket created successfully
ESCALATED         # Routed to human reviewer
PENDING_CLARIFICATION  # Awaiting user clarification
KB_ONLY           # No ticket created, KB articles provided
ERROR             # Processing error occurred
```

### EscalationReason
```
CONFIDENCE_TOO_LOW          # confidence < 0.70
POLICY_KEYWORD_DETECTED     # appeal, waiver, refund, etc.
SENSITIVE_TOPIC             # Title IX, mental health, threats
MULTI_DEPARTMENT            # Requires coordination
USER_REQUESTED_HUMAN        # Explicit human request
MAX_CLARIFICATIONS_EXCEEDED # 3 failed disambiguation attempts
```

### IntentCategory
```
ACCOUNT_ACCESS       # password_reset, login_issues, account_locked
ACADEMIC_RECORDS     # transcript_request, grade_inquiry, enrollment_verification
FINANCIAL            # financial_aid_inquiry, tuition_payment, refund_request
FACILITIES           # facilities_issue, maintenance_request, room_booking
ENROLLMENT           # course_enrollment, add_drop, registration_hold
STUDENT_SERVICES     # parking_permit, id_card, housing
POLICY_EXCEPTION     # grade_appeal, withdrawal_request, waiver_request
GENERAL_INQUIRY      # general_question, department_contact
STATUS_CHECK         # ticket_status, request_followup
HUMAN_REQUEST        # request_human, speak_to_person
```

---

## Relationships

```
Session 1 ──────── * AuditLog
    │                   (session_id reference)
    │
    └── conversation_history[]
            │
            └── ticket_id ──── * Ticket (external: ServiceNow)

QueryResult ─── feeds ──→ RoutingDecision ─── feeds ──→ ActionResult
    (QueryAgent)              (RouterAgent)              (ActionAgent)
```

---

## State Transitions

### Session Lifecycle

```
┌─────────────┐    First message    ┌─────────────┐
│   (none)    │ ─────────────────→  │   ACTIVE    │
└─────────────┘                     └─────────────┘
                                          │
                        ┌─────────────────┼─────────────────┐
                        │                 │                 │
                        ▼                 ▼                 ▼
                   New message       90 days TTL      User logs out
                   (reset timer)      expires
                        │                 │                 │
                        │                 ▼                 ▼
                        │           ┌─────────────┐   ┌─────────────┐
                        └──────────→│   EXPIRED   │   │   CLOSED    │
                                    └─────────────┘   └─────────────┘
```

### Clarification Flow

```
┌─────────────────┐   confidence < 0.70   ┌─────────────────┐
│  Query received │ ────────────────────→ │ Ask clarification│
└─────────────────┘                       └─────────────────┘
                                                  │
                              ┌───────────────────┼───────────────────┐
                              │                   │                   │
                              ▼                   ▼                   ▼
                        User clarifies      attempts >= 3      User abandons
                              │                   │                   │
                              ▼                   ▼                   ▼
                      ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
                      │ Re-classify  │    │   ESCALATE   │    │   (closed)   │
                      └──────────────┘    └──────────────┘    └──────────────┘
```

---

## Privacy Considerations

1. **Student ID Hashing**: All stored student IDs use SHA-256 hashing
   ```python
   student_id_hash = hashlib.sha256(student_id.encode()).hexdigest()
   ```

2. **PII in Queries**: Raw query text containing PII is:
   - Processed in memory only
   - NOT stored in Session.conversation_history
   - NOT stored in AuditLog
   - Replaced with intent classification result

3. **Audit Log Scope**: Captures routing decisions without sensitive content:
   - Intent: ✅ Stored
   - Department: ✅ Stored
   - Raw query: ❌ Not stored
   - Student name: ❌ Not stored

---

## Indexes

### Session Collection (Cosmos DB)
- **Partition key**: `student_id_hash`
- **Indexes**: `created_at`, `last_active`

### AuditLog Collection (Cosmos DB)
- **Partition key**: `timestamp` (by day for time-series queries)
- **Indexes**: `student_id_hash`, `detected_intent`, `routed_department`, `escalated`

### Knowledge Base (Azure AI Search)
- **Key field**: `article_id`
- **Searchable fields**: `title`, `content`
- **Filterable fields**: `department`, `last_updated`
- **Semantic configuration**: Enabled on `title`, `content`
