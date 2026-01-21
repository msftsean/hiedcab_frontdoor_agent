# Tasks: Universal Front Door Support Agent

**Input**: Design documents from `/specs/1-front-door-agent/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/api.yaml

**Tests**: Tests are included per Constitution Principle V (Test-First Development).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create backend project structure with directories: src/agents/, src/models/, src/services/, src/api/, src/config/ in backend/
- [ ] T002 [P] Initialize Python project with pyproject.toml and requirements.txt in backend/
- [ ] T003 [P] Create frontend project with Vite, React 18, TypeScript in frontend/
- [ ] T004 [P] Configure Tailwind CSS with custom theme variables in frontend/tailwind.config.js
- [ ] T005 [P] Create backend/.env.example with all required environment variables
- [ ] T006 [P] Create frontend/.env.example with VITE_API_URL
- [ ] T007 [P] Configure pytest with conftest.py and fixtures in backend/tests/conftest.py
- [ ] T008 [P] Configure Jest and React Testing Library in frontend/package.json
- [ ] T009 Create mock data files: sample_tickets.json, sample_kb_articles.json, intent_examples.json in backend/mock_data/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T010 Create shared enumerations (Department, Priority, Sentiment, ActionStatus, EscalationReason, IntentCategory) in backend/src/models/enums.py
- [ ] T011 [P] Create base model classes with Pydantic validation in backend/src/models/base.py
- [ ] T012 [P] Create Settings class with environment configuration in backend/src/config/settings.py
- [ ] T013 [P] Create few-shot prompt template for intent classification in backend/src/config/prompts/intent_classification.txt
- [ ] T014 Create LLMService interface and mock implementation in backend/src/services/llm_service.py
- [ ] T015 [P] Create TicketService interface and mock implementation in backend/src/services/ticket_service.py
- [ ] T016 [P] Create KnowledgeService interface and mock implementation in backend/src/services/knowledge_service.py
- [ ] T017 [P] Create SessionService interface and mock implementation in backend/src/services/session_service.py
- [ ] T018 Create PIIDetector service with regex patterns in backend/src/services/pii_detector.py
- [ ] T019 Create AuditService for logging routing decisions in backend/src/services/audit_service.py
- [ ] T020 Create FastAPI app entry point with CORS and middleware setup in backend/src/api/main.py
- [ ] T021 [P] Create SSO auth middleware (mock for dev, real JWT validation for prod) in backend/src/api/middleware/auth.py
- [ ] T022 [P] Create rate limiting middleware in backend/src/api/middleware/rate_limit.py
- [ ] T023 [P] Create health check endpoint (GET /api/health) in backend/src/api/routes/health.py
- [ ] T024 Create frontend API client service with axios/fetch wrapper in frontend/src/services/api.ts
- [ ] T025 [P] Create useAccessibility hook for high-contrast mode toggle in frontend/src/hooks/useAccessibility.ts
- [ ] T026 [P] Create global styles and high-contrast CSS variables in frontend/src/styles/globals.css and frontend/src/styles/high-contrast.css
- [ ] T027 Write unit tests for PIIDetector in backend/tests/unit/test_pii_detector.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Submit Standard Support Request (Priority: P1) 🎯 MVP

**Goal**: Student submits a query → system detects intent → routes to department → creates ticket → returns KB articles

**Independent Test**: Submit "I forgot my password" and verify ticket ID, IT department routing, and KB articles within 30 seconds

### Models for User Story 1

- [ ] T028 [P] [US1] Create QueryResult model with intent, entities, confidence, pii_detected, sentiment in backend/src/models/query_result.py
- [ ] T029 [P] [US1] Create RoutingDecision model with department, priority, escalate_to_human, sla in backend/src/models/routing_decision.py
- [ ] T030 [P] [US1] Create ActionResult model with ticket_id, department, status, knowledge_articles, message in backend/src/models/action_result.py
- [ ] T031 [P] [US1] Create KnowledgeArticle model with article_id, title, url, relevance_score in backend/src/models/knowledge_article.py
- [ ] T032 [P] [US1] Create Session model with session_id, student_id_hash, conversation_history in backend/src/models/session.py
- [ ] T033 [P] [US1] Create AuditLog model with all audit fields in backend/src/models/audit_log.py

### Agents for User Story 1

- [ ] T034 [US1] Create QueryAgent with analyze() method for intent detection and entity extraction in backend/src/agents/query_agent.py
- [ ] T035 [US1] Create RouterAgent with route() method for department routing (standard routing only, no escalation yet) in backend/src/agents/router_agent.py
- [ ] T036 [US1] Create ActionAgent with execute() method for ticket creation and KB retrieval in backend/src/agents/action_agent.py

### API for User Story 1

- [ ] T037 [US1] Create POST /api/chat endpoint with full agent pipeline in backend/src/api/routes/chat.py

### Frontend for User Story 1

- [ ] T038 [P] [US1] Create MessageBubble component for chat messages in frontend/src/components/MessageBubble.tsx
- [ ] T039 [P] [US1] Create TypingIndicator component for processing state in frontend/src/components/TypingIndicator.tsx
- [ ] T040 [P] [US1] Create TicketCard component to display ticket ID with copy button in frontend/src/components/TicketCard.tsx
- [ ] T041 [P] [US1] Create KnowledgeArticleCard component for KB article display in frontend/src/components/KnowledgeArticleCard.tsx
- [ ] T042 [US1] Create useChat hook for chat state management and API calls in frontend/src/hooks/useChat.ts
- [ ] T043 [US1] Create ChatWindow component integrating all chat UI elements in frontend/src/components/ChatWindow.tsx
- [ ] T044 [US1] Create ChatPage as main page component in frontend/src/pages/ChatPage.tsx
- [ ] T045 [US1] Update App.tsx with routing and ChatPage in frontend/src/App.tsx

### Tests for User Story 1

- [ ] T046 [P] [US1] Write unit tests for QueryAgent intent detection in backend/tests/unit/test_query_agent.py
- [ ] T047 [P] [US1] Write unit tests for RouterAgent routing logic in backend/tests/unit/test_router_agent.py
- [ ] T048 [P] [US1] Write unit tests for ActionAgent ticket creation in backend/tests/unit/test_action_agent.py
- [ ] T049 [US1] Write integration test for full chat flow (password reset scenario) in backend/tests/integration/test_chat_flow.py
- [ ] T050 [US1] Write contract test for POST /api/chat endpoint in backend/tests/contract/test_api_contracts.py

**Checkpoint**: User Story 1 complete - students can submit standard requests and receive tickets with KB articles

---

## Phase 4: User Story 2 - Receive Escalation for Policy-Related Requests (Priority: P2)

**Goal**: Policy keywords (refund, appeal, waiver) trigger human escalation with appropriate messaging

**Independent Test**: Submit "I want to appeal my grade" and verify escalation flag, human review message

### Implementation for User Story 2

- [ ] T051 [US2] Add policy keyword detection to QueryAgent (appeal, waiver, exception, override, refund) in backend/src/agents/query_agent.py
- [ ] T052 [US2] Add sensitive topic detection to QueryAgent (Title IX, mental health, threats) in backend/src/agents/query_agent.py
- [ ] T053 [US2] Implement escalation logic in RouterAgent for policy_keyword_detected trigger in backend/src/agents/router_agent.py
- [ ] T054 [US2] Implement escalation logic in RouterAgent for sensitive_topic trigger in backend/src/agents/router_agent.py
- [ ] T055 [US2] Update ActionAgent to generate escalation messages with SLA expectations in backend/src/agents/action_agent.py
- [ ] T056 [P] [US2] Update ChatWindow to display escalation status clearly in frontend/src/components/ChatWindow.tsx
- [ ] T057 [P] [US2] Create HumanEscalationButton component (always visible per FR-029) in frontend/src/components/HumanEscalationButton.tsx

### Tests for User Story 2

- [ ] T058 [P] [US2] Write unit tests for policy keyword escalation in backend/tests/unit/test_router_agent.py
- [ ] T059 [P] [US2] Write unit tests for sensitive topic escalation in backend/tests/unit/test_router_agent.py
- [ ] T060 [US2] Write integration test for escalation flow (grade appeal scenario) in backend/tests/integration/test_escalation.py

**Checkpoint**: User Story 2 complete - policy-related requests correctly escalate to human review

---

## Phase 5: User Story 3 - Track Existing Request Status (Priority: P3)

**Goal**: Student asks "What's the status of my ticket?" and receives current ticket status

**Independent Test**: Create ticket, then ask status and verify correct status returned

### Implementation for User Story 3

- [ ] T061 [US3] Add ticket_status intent detection to QueryAgent in backend/src/agents/query_agent.py
- [ ] T062 [US3] Add status check routing logic to RouterAgent in backend/src/agents/router_agent.py
- [ ] T063 [US3] Implement ticket lookup in ActionAgent using session history in backend/src/agents/action_agent.py
- [ ] T064 [US3] Create GET /api/tickets/{ticket_id} endpoint in backend/src/api/routes/tickets.py
- [ ] T065 [US3] Create GET /api/tickets endpoint for listing user's tickets in backend/src/api/routes/tickets.py
- [ ] T066 [US3] Update ChatWindow to handle status check responses in frontend/src/components/ChatWindow.tsx

### Tests for User Story 3

- [ ] T067 [P] [US3] Write unit tests for ticket_status intent detection in backend/tests/unit/test_query_agent.py
- [ ] T068 [US3] Write integration test for multi-turn status check flow in backend/tests/integration/test_chat_flow.py
- [ ] T069 [US3] Write contract tests for GET /api/tickets endpoints in backend/tests/contract/test_api_contracts.py

**Checkpoint**: User Story 3 complete - students can check status of existing tickets

---

## Phase 6: User Story 4 - Clarify Ambiguous Requests (Priority: P4)

**Goal**: Low-confidence queries trigger clarification questions instead of misrouting

**Independent Test**: Submit "I need help with my account" and verify clarification question returned

### Implementation for User Story 4

- [ ] T070 [US4] Implement confidence threshold check (< 0.70) in RouterAgent in backend/src/agents/router_agent.py
- [ ] T071 [US4] Add clarification question generation to ActionAgent in backend/src/agents/action_agent.py
- [ ] T072 [US4] Implement clarification_attempts tracking in SessionService in backend/src/services/session_service.py
- [ ] T073 [US4] Add max_clarifications_exceeded escalation trigger (3 attempts) in RouterAgent in backend/src/agents/router_agent.py
- [ ] T074 [US4] Update chat endpoint to handle PENDING_CLARIFICATION status in backend/src/api/routes/chat.py
- [ ] T075 [US4] Update ChatWindow to display clarification questions with response options in frontend/src/components/ChatWindow.tsx

### Tests for User Story 4

- [ ] T076 [P] [US4] Write unit tests for confidence threshold trigger in backend/tests/unit/test_router_agent.py
- [ ] T077 [P] [US4] Write unit tests for clarification_attempts tracking in backend/tests/unit/test_session_service.py
- [ ] T078 [US4] Write integration test for clarification flow with re-classification in backend/tests/integration/test_chat_flow.py

**Checkpoint**: User Story 4 complete - ambiguous queries receive clarification instead of misrouting

---

## Phase 7: User Story 5 - Request Human Assistance (Priority: P5)

**Goal**: Explicit human requests ("I need to talk to a person") immediately escalate

**Independent Test**: Submit "I need to talk to a person" and verify immediate escalation

### Implementation for User Story 5

- [ ] T079 [US5] Add request_human intent detection to QueryAgent in backend/src/agents/query_agent.py
- [ ] T080 [US5] Implement user_requested_human escalation trigger in RouterAgent in backend/src/agents/router_agent.py
- [ ] T081 [US5] Add human request response with wait time estimate in ActionAgent in backend/src/agents/action_agent.py
- [ ] T082 [US5] Update HumanEscalationButton to trigger immediate escalation in frontend/src/components/HumanEscalationButton.tsx

### Tests for User Story 5

- [ ] T083 [P] [US5] Write unit tests for request_human intent detection in backend/tests/unit/test_query_agent.py
- [ ] T084 [US5] Write integration test for human request flow in backend/tests/integration/test_escalation.py

**Checkpoint**: User Story 5 complete - explicit human requests immediately escalate

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T085 [P] Create AccessibilityToggle component for high-contrast mode in frontend/src/components/AccessibilityToggle.tsx
- [ ] T086 [P] Add ARIA labels and keyboard navigation to all components in frontend/src/components/
- [ ] T087 [P] Add mobile responsive styles to ChatWindow in frontend/src/components/ChatWindow.tsx
- [ ] T088 [P] Implement graceful degradation for LLM service unavailable in backend/src/agents/query_agent.py
- [ ] T089 [P] Implement graceful degradation for ticketing service unavailable in backend/src/agents/action_agent.py
- [ ] T090 [P] Implement graceful degradation for KB service unavailable in backend/src/agents/action_agent.py
- [ ] T091 Create Dockerfile for backend in backend/Dockerfile
- [ ] T092 [P] Create Dockerfile for frontend in frontend/Dockerfile
- [ ] T093 Write E2E tests with Playwright for complete chat flow in frontend/tests/e2e/chat.spec.ts
- [ ] T094 Run accessibility audit with axe-core and fix violations in frontend/
- [ ] T095 Run quickstart.md validation scenarios and verify all pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

| Story | Depends On | Can Start After |
|-------|------------|-----------------|
| US1 (P1) | Foundational | Phase 2 complete |
| US2 (P2) | Foundational | Phase 2 complete (independent of US1) |
| US3 (P3) | US1 | US1 creates tickets to check |
| US4 (P4) | Foundational | Phase 2 complete (independent of US1) |
| US5 (P5) | Foundational | Phase 2 complete (independent of US1) |

### Within Each User Story

1. Models before agents
2. Agents before API endpoints
3. API endpoints before frontend components
4. Frontend components before hooks
5. Hooks before pages
6. Tests written alongside implementation (not strictly before for velocity)

### Parallel Opportunities

**Phase 1 (Setup)**:
```
T002, T003, T004, T005, T006, T007, T008 can all run in parallel
```

**Phase 2 (Foundational)**:
```
After T010:
  T011, T012, T013 in parallel
After T014:
  T015, T016, T017 in parallel
After T020:
  T021, T022, T023 in parallel
```

**Phase 3 (US1)**:
```
All models T028-T033 in parallel
After models:
  T034, T035, T036 sequential (agent dependencies)
After T037:
  T038, T039, T040, T041 in parallel (frontend components)
Tests T046, T047, T048 in parallel
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test "I forgot my password" flow end-to-end
5. Deploy/demo if ready - this is a working MVP

### Incremental Delivery

| Increment | Stories | Value Delivered |
|-----------|---------|-----------------|
| MVP | US1 | Students can submit requests and get tickets |
| +Escalation | US2 | Policy requests safely escalate to humans |
| +Status | US3 | Students can check ticket status |
| +Clarification | US4 | Ambiguous queries get clarified |
| +Human | US5 | Explicit human requests honored |

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (1-2 days)
2. Once Foundational is done:
   - Developer A: User Story 1 (P1) - core flow
   - Developer B: User Story 2 (P2) - escalation
   - Developer C: User Story 4 (P4) - clarification
3. After US1: Developer A picks up US3 (depends on tickets)
4. After US2/US4: Developers pick up US5 and Polish

---

## Summary

| Phase | Tasks | Parallel | Story |
|-------|-------|----------|-------|
| Phase 1: Setup | 9 | 7 | - |
| Phase 2: Foundational | 18 | 12 | - |
| Phase 3: US1 | 23 | 15 | Submit Standard Request |
| Phase 4: US2 | 10 | 4 | Policy Escalation |
| Phase 5: US3 | 9 | 2 | Track Status |
| Phase 6: US4 | 9 | 3 | Clarify Ambiguous |
| Phase 7: US5 | 6 | 2 | Request Human |
| Phase 8: Polish | 11 | 7 | - |
| **Total** | **95** | **52** | |

**MVP Scope**: Phases 1-3 (50 tasks) delivers a working system for standard support requests.

**Suggested First Sprint**: Complete through US1 (Phase 3) for demo-ready MVP.
