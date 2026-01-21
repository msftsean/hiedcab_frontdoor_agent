# Quickstart: Universal Front Door Support Agent

**Date**: 2026-01-20
**Feature**: 1-front-door-agent

## Overview

This guide covers how to run and test the Front Door Support Agent locally and in production.

---

## Prerequisites

### Required Software
- Python 3.11+
- Node.js 18+
- Docker (optional, for containerized deployment)

### Required Accounts/Credentials
- Azure subscription with:
  - Azure OpenAI service (GPT-4o deployment)
  - Azure Cosmos DB account
  - Azure AI Search service
- ServiceNow developer instance (or use mock mode)

---

## Local Development Setup

### 1. Clone and Install

```bash
# Clone repository
git clone https://github.com/university/front-door-agent.git
cd front-door-agent

# Backend setup
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### 2. Environment Configuration

Create `backend/.env`:

```env
# Mode: "mock" for demo, "production" for real services
MODE=mock

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-instance.openai.azure.com
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o

# Azure Cosmos DB
COSMOS_ENDPOINT=https://your-instance.documents.azure.com:443/
COSMOS_KEY=your-cosmos-key
COSMOS_DATABASE=frontdoor
COSMOS_CONTAINER_SESSIONS=sessions
COSMOS_CONTAINER_AUDIT=audit_logs

# Azure AI Search
SEARCH_ENDPOINT=https://your-instance.search.windows.net
SEARCH_KEY=your-search-key
SEARCH_INDEX=knowledge-articles

# ServiceNow (ignored in mock mode)
SERVICENOW_INSTANCE=your-instance.service-now.com
SERVICENOW_CLIENT_ID=your-client-id
SERVICENOW_CLIENT_SECRET=your-client-secret

# SSO (for development, use mock auth)
SSO_ISSUER=https://sso.university.edu
SSO_AUDIENCE=front-door-agent
```

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

### 3. Start Services

**Terminal 1 - Backend:**
```bash
cd backend
source .venv/bin/activate
uvicorn src.api.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Access the application at `http://localhost:5173`

---

## Mock Mode Testing

Mock mode simulates all external services for demo and testing:

### Test Scenarios

**1. Standard Support Request (P1)**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer mock-student-token" \
  -d '{"message": "I forgot my password"}'
```

Expected response:
```json
{
  "session_id": "...",
  "ticket_id": "TKT-IT-20260120-0001",
  "department": "IT",
  "status": "created",
  "message": "I've created a ticket for IT Support...",
  "knowledge_articles": [
    {"title": "How to Reset Your Password", "relevance_score": 0.94}
  ],
  "escalated": false,
  "estimated_response_time": "2 hours"
}
```

**2. Policy Escalation (P2)**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer mock-student-token" \
  -d '{"message": "I want to appeal my grade"}'
```

Expected response:
```json
{
  "session_id": "...",
  "ticket_id": "TKT-REG-20260120-0001",
  "department": "REGISTRAR",
  "status": "escalated",
  "message": "Your request requires review by the Registrar's Office...",
  "escalated": true,
  "escalation_reason": "policy_keyword_detected",
  "estimated_response_time": "1 business day"
}
```

**3. Ambiguous Query (P4)**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer mock-student-token" \
  -d '{"message": "I need help with my account"}'
```

Expected response:
```json
{
  "session_id": "...",
  "status": "pending_clarification",
  "message": "I want to help you with your account. Are you referring to your university login account, your financial account, or something else?",
  "escalated": false
}
```

**4. Multi-turn Conversation (P3)**
```bash
# First message
RESPONSE=$(curl -s -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer mock-student-token" \
  -d '{"message": "I forgot my password"}')

SESSION_ID=$(echo $RESPONSE | jq -r '.session_id')

# Follow-up message
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer mock-student-token" \
  -d "{\"message\": \"What's the status of my ticket?\", \"session_id\": \"$SESSION_ID\"}"
```

---

## Running Tests

### Backend Tests
```bash
cd backend
source .venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/                    # Unit tests only
pytest tests/integration/             # Integration tests only
pytest tests/contract/                # API contract tests
pytest -m "escalation"                # Tests marked with @pytest.mark.escalation
```

### Frontend Tests
```bash
cd frontend

# Unit tests
npm test

# E2E tests (requires backend running)
npm run test:e2e
```

### Accessibility Tests
```bash
cd frontend
npm run test:a11y  # Runs axe-core accessibility checks
```

---

## Integration Scenarios

### Scenario 1: Complete Support Flow

```gherkin
Feature: Standard Support Request

Scenario: Student requests password reset
  Given a student is authenticated
  When they send "I forgot my password and can't log into Canvas"
  Then the system should:
    - Detect intent: password_reset
    - Extract entity: system=Canvas
    - Route to: IT department
    - Create ticket: TKT-IT-YYYYMMDD-XXXX
    - Return KB articles about password reset
    - Respond within 30 seconds
```

### Scenario 2: Escalation Flow

```gherkin
Feature: Policy Escalation

Scenario: Student requests grade appeal
  Given a student is authenticated
  When they send "I want to appeal my grade in CS101"
  Then the system should:
    - Detect intent: grade_appeal
    - Detect policy keyword: "appeal"
    - Set escalate_to_human: true
    - Create escalation ticket
    - Inform student human review required
```

### Scenario 3: Graceful Degradation

```gherkin
Feature: Service Unavailability

Scenario: LLM service unavailable
  Given the LLM service is down
  When a student sends a query
  Then the system should:
    - Use keyword-based fallback routing
    - Create ticket if possible
    - Escalate to human if unsure
    - Inform student of limited functionality
```

---

## Health Monitoring

Check system health:
```bash
curl http://localhost:8000/api/health
```

Response when healthy:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-20T10:30:00Z",
  "services": {
    "llm": {"status": "up", "latency_ms": 150},
    "ticketing": {"status": "up", "latency_ms": 80},
    "knowledge_base": {"status": "up", "latency_ms": 45},
    "session_store": {"status": "up", "latency_ms": 20}
  }
}
```

Response when degraded:
```json
{
  "status": "degraded",
  "timestamp": "2026-01-20T10:30:00Z",
  "services": {
    "llm": {"status": "down", "error": "Connection timeout"},
    "ticketing": {"status": "up", "latency_ms": 80},
    "knowledge_base": {"status": "up", "latency_ms": 45},
    "session_store": {"status": "up", "latency_ms": 20}
  }
}
```

---

## Production Deployment

### Azure Container Apps

```bash
# Build and push images
az acr build --registry yourregistry --image frontdoor-backend:latest ./backend
az acr build --registry yourregistry --image frontdoor-frontend:latest ./frontend

# Deploy backend
az containerapp create \
  --name frontdoor-backend \
  --resource-group frontdoor-rg \
  --environment frontdoor-env \
  --image yourregistry.azurecr.io/frontdoor-backend:latest \
  --target-port 8000 \
  --ingress external \
  --min-replicas 2 \
  --max-replicas 10

# Deploy frontend
az containerapp create \
  --name frontdoor-frontend \
  --resource-group frontdoor-rg \
  --environment frontdoor-env \
  --image yourregistry.azurecr.io/frontdoor-frontend:latest \
  --target-port 80 \
  --ingress external
```

### Environment Variables (Production)

Set via Azure Container Apps secrets or Key Vault references:

```bash
az containerapp secret set \
  --name frontdoor-backend \
  --resource-group frontdoor-rg \
  --secrets \
    azure-openai-key=keyvaultref:... \
    cosmos-key=keyvaultref:... \
    servicenow-secret=keyvaultref:...
```

---

## Troubleshooting

### Common Issues

**1. "Authentication failed" error**
- Check SSO token is valid and not expired
- Verify SSO_ISSUER and SSO_AUDIENCE in .env

**2. "LLM service unavailable"**
- Check AZURE_OPENAI_ENDPOINT is correct
- Verify API key has access to the deployment
- Check deployment name matches AZURE_OPENAI_DEPLOYMENT

**3. "Ticket creation failed"**
- In mock mode: Check mock_data/sample_tickets.json exists
- In production: Verify ServiceNow credentials and permissions

**4. "Session not found"**
- Session may have expired (90-day TTL)
- Verify COSMOS_CONTAINER_SESSIONS is correct

### Logging

View backend logs:
```bash
# Local
uvicorn src.api.main:app --log-level debug

# Production (Azure)
az containerapp logs show --name frontdoor-backend --resource-group frontdoor-rg
```

### Debug Mode

Enable detailed logging in `backend/.env`:
```env
LOG_LEVEL=DEBUG
LOG_FORMAT=json
```

---

## Next Steps

1. Run `/speckit.tasks` to generate implementation task list
2. Set up CI/CD pipeline for automated testing
3. Configure Azure Monitor for production observability
4. Schedule accessibility audit with university accessibility office
