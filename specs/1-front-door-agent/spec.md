# Feature Specification: Universal Front Door Support Agent

**Feature Branch**: `1-front-door-agent`
**Created**: 2026-01-20
**Status**: Draft
**Input**: User description: "Universal Front Door Support Agent - Three-agent system for routing student support requests to correct departments, creating tickets, retrieving knowledge, and escalating complex issues to humans"

## Problem Statement

Universities suffer from a "47 front doors" problem where students must navigate multiple disconnected support channels. Students are transferred 3+ times on average, must re-explain their problem at each handoff, don't know which department handles their issue, wait times exceed 20 minutes, and after-hours requests go unanswered. Current first-contact resolution rate is only 40%.

## Vision

Create a single, intelligent entry point that receives any student support request, detects intent, routes to the correct department, creates tickets in appropriate systems, retrieves relevant knowledge, and escalates complex or policy-related issues to humans—eliminating the "47 front doors" problem and increasing first-contact resolution from 40% to 65%.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Submit Standard Support Request (Priority: P1)

A student has a common support issue (password reset, transcript request, facilities report) and needs quick resolution without knowing which department to contact.

**Why this priority**: This represents 80%+ of all support requests. Solving standard routing correctly delivers immediate value to most students and validates the core intent detection and routing logic.

**Independent Test**: Can be fully tested by submitting a standard query like "I forgot my password" and verifying the system returns a ticket ID, correct department routing, and relevant knowledge articles within 30 seconds.

**Acceptance Scenarios**:

1. **Given** a student is logged in, **When** they submit "I forgot my password", **Then** the system creates a ticket routed to IT, returns a ticket ID, and displays relevant password reset articles.
2. **Given** a student submits "The elevator in Smith Hall is broken", **When** processed, **Then** the system extracts "Smith Hall" as a building entity and routes to Facilities with appropriate priority.
3. **Given** a student submits "I need a transcript for grad school", **When** processed, **Then** the system routes to Registrar and provides knowledge articles about transcript requests.
4. **Given** a student submits a request after business hours, **When** processed, **Then** the system still creates a ticket, provides knowledge articles, and sets appropriate SLA expectations.

---

### User Story 2 - Receive Escalation for Policy-Related Requests (Priority: P2)

A student has a request that requires human judgment (appeals, waivers, exceptions, refunds) and needs their issue properly documented and routed to a human reviewer.

**Why this priority**: Policy decisions cannot be automated and require human judgment. Proper escalation prevents the agent from making unauthorized decisions while ensuring students' requests are properly captured.

**Independent Test**: Can be tested by submitting "I want to appeal my grade" and verifying the system flags for human escalation, creates an escalation ticket, and clearly communicates that human review is required.

**Acceptance Scenarios**:

1. **Given** a student submits "Can I get a refund for this semester?", **When** the system detects "refund" as a policy keyword, **Then** it escalates to human review and informs the student a human will respond.
2. **Given** a student submits "I want to appeal my grade", **When** processed, **Then** the system creates an escalation ticket and provides expected response time for human review.
3. **Given** a student mentions Title IX, mental health crisis, or threat assessment keywords, **When** detected, **Then** the system immediately escalates to appropriate human handlers with urgent priority.

---

### User Story 3 - Track Existing Request Status (Priority: P3)

A student has previously submitted a request and wants to check its status without calling or re-explaining their issue.

**Why this priority**: Status tracking improves student satisfaction and reduces repeat contacts to support staff. Requires session history to function properly.

**Independent Test**: Can be tested by submitting a query, receiving a ticket ID, then asking "What's the status of my ticket?" and receiving accurate status information.

**Acceptance Scenarios**:

1. **Given** a student previously received ticket TKT-IT-123, **When** they ask "What's the status of my ticket?", **Then** the system retrieves the current status from the ticketing system.
2. **Given** a student has multiple open tickets, **When** they ask about status, **Then** the system lists all their recent tickets with status.

---

### User Story 4 - Clarify Ambiguous Requests (Priority: P4)

A student submits a vague request that could apply to multiple departments and needs the system to ask for clarification rather than misrouting.

**Why this priority**: Handling ambiguity correctly prevents misrouting and frustration. A follow-up clarification is better than wrong routing.

**Independent Test**: Can be tested by submitting "I need help with my account" and verifying the system asks a clarifying question rather than guessing incorrectly.

**Acceptance Scenarios**:

1. **Given** a student submits "I need help with my account", **When** the confidence score is below 0.70, **Then** the system asks "Are you referring to your university login account, your financial account, or something else?"
2. **Given** a student provides clarification after being asked, **When** the clarified intent is processed, **Then** the system routes to the correct department with the full conversation context preserved.
3. **Given** the system cannot resolve ambiguity after 3 clarification attempts, **When** this threshold is reached, **Then** it escalates to human triage.

---

### User Story 5 - Request Human Assistance (Priority: P5)

A student explicitly wants to speak with a human rather than interact with the automated system.

**Why this priority**: Respecting user preference for human contact is essential for trust. Some issues genuinely require human empathy or complex explanation.

**Independent Test**: Can be tested by saying "I need to talk to a person" and verifying immediate escalation to human queue.

**Acceptance Scenarios**:

1. **Given** a student says "I need to talk to a person", **When** processed, **Then** the system immediately routes to human queue without further automated interaction.
2. **Given** escalation to human is triggered, **When** completed, **Then** the system provides estimated wait time and confirms a human will respond.

---

### Edge Cases

- What happens when a query contains PII (social security numbers, financial data)?
  - System flags PII for secure handling and does not log the raw query content
- How does the system handle queries that span multiple departments (e.g., "My financial aid affects my enrollment")?
  - System detects multi-department coordination need and escalates to human triage
- What happens when sentiment analysis detects high frustration?
  - System increases priority and may proactively offer human escalation
- How does the system handle non-English queries?
  - v1 supports English only; non-English queries receive a message directing to multilingual support line
- What happens if external systems (ticketing, knowledge base) are unavailable?
  - System gracefully degrades: provides best available information and logs for retry, informs user of limited functionality
- What happens if SSO authentication is unavailable?
  - System allows read-only knowledge base browsing; ticket creation and personalized features are blocked until authentication is restored

## Requirements *(mandatory)*

### Functional Requirements

**Intent Detection & Entity Extraction**
- **FR-001**: System MUST analyze natural language queries and detect intent from 30+ categories including: password_reset, transcript_request, financial_aid_inquiry, facilities_issue, grade_appeal, course_enrollment, parking_permit (using LLM-based classification with few-shot prompting)
- **FR-002**: System MUST extract entities from queries including: building names, course codes, dates, urgency indicators
- **FR-003**: System MUST calculate a confidence score (0.0-1.0) for each intent detection
- **FR-004**: System MUST detect PII in queries and flag for secure handling (not logged in plain text)
- **FR-005**: System MUST analyze sentiment to detect frustrated or urgent tones

**Routing & Decision Making**
- **FR-006**: System MUST route queries to one of these departments: IT, HR, Registrar, Financial Aid, Facilities, Student Affairs, Campus Safety, or ESCALATE_TO_HUMAN
- **FR-007**: System MUST escalate to human when confidence score is below 0.70
- **FR-008**: System MUST escalate to human when policy keywords are detected: appeal, waiver, exception, override, refund, withdrawal deadline
- **FR-009**: System MUST escalate to human for sensitive topics: Title IX, mental health crisis, threat assessment, discrimination
- **FR-010**: System MUST escalate to human when multi-department coordination is needed
- **FR-011**: System MUST escalate to human when user explicitly requests human contact
- **FR-012**: System MUST escalate to human after 3 failed clarification attempts
- **FR-013**: System MUST assign priority levels (low, medium, high, urgent) based on urgency indicators and sentiment
- **FR-014**: System MUST set appropriate SLA expectations based on department and priority

**Ticket Creation & Knowledge Retrieval**
- **FR-015**: System MUST create tickets in the university ticketing system with: ticket ID (format: TKT-{DEPT}-{YYYYMMDD}-{SEQ}), department, priority, description, student context
- **FR-016**: System MUST retrieve top 3 relevant knowledge base articles for each query
- **FR-017**: System MUST display knowledge articles with title, URL, and relevance indicator

**Session & Audit**
- **FR-018**: System MUST maintain session context across multi-turn conversations (stateful)
- **FR-019**: System MUST store session history including: student_id (hashed), conversation intents, ticket IDs created
- **FR-020**: System MUST log audit trail: user_id, query timestamp, detected intent, routed department, ticket_id, PII flag, escalation status
- **FR-021**: System MUST NOT log raw query text containing PII beyond audit requirements

**Boundaries (What System Must NOT Do)**
- **FR-022**: System MUST NOT approve refunds, waivers, or policy exceptions
- **FR-023**: System MUST NOT modify student records (grades, enrollment, financial data)
- **FR-024**: System MUST NOT access FERPA-protected data beyond routing context
- **FR-025**: System MUST NOT bypass human review for policy-related queries
- **FR-026**: System MUST NOT make enrollment or financial decisions

**User Interface**
- **FR-027**: System MUST provide a web chat interface accessible 24/7
- **FR-028**: System MUST display ticket ID prominently with ability to copy
- **FR-029**: System MUST always display option to speak to a human
- **FR-030**: System MUST provide high-contrast mode for accessibility (WCAG compliance)
- **FR-031**: System MUST be responsive for mobile devices
- **FR-032**: System MUST show typing indicators during processing

### Non-Functional Requirements

- **NFR-001**: System MUST respond with ticket ID and initial guidance within 30 seconds
- **NFR-002**: System MUST be available 24/7 (target 99.9% uptime during pilot)
- **NFR-003**: System MUST support students: undergraduate, graduate, online, continuing education
- **NFR-004**: Session history MUST be retained for 90 days before anonymization for analytics
- **NFR-005**: System MUST handle 500 concurrent users during peak registration periods

### Key Entities

- **Session**: Represents a student's conversation context including session_id, student_id (hashed for privacy), creation timestamp, last activity timestamp, and conversation history (list of turns with intents and ticket IDs)
- **AuditLog**: Represents an immutable record of each interaction including log_id, timestamp, student_id (hashed), detected intent, routed department, ticket_id, escalation status, PII detection flag, and sentiment classification
- **QueryResult**: Represents the output of intent analysis including detected intent, suggested department, extracted entities, confidence score, escalation flag, PII detection flag, and sentiment
- **RoutingDecision**: Represents the routing determination including target department, priority level, escalation flag with reason, and suggested SLA
- **ActionResult**: Represents the outcome of executing a request including ticket_id, department, status, knowledge articles retrieved, estimated response time, escalation status, and user-facing message
- **KnowledgeArticle**: Represents a relevant help article including title, URL, and relevance score

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: First-contact resolution rate improves from 40% to 65% (queries resolved without human transfer)
- **SC-002**: Students receive correct routing, ticket ID, and initial guidance within 30 seconds
- **SC-003**: System operates 24/7, handling after-hours requests that previously went unanswered
- **SC-004**: Average handling time decreases from 8 minutes to under 1 minute for standard requests
- **SC-005**: Student satisfaction score improves from 3.2/5 to 4.5/5 (post-interaction survey)
- **SC-006**: Escalation rate for automated decisions stays below 20%
- **SC-007**: Routing accuracy exceeds 90% (validated via human review of sample)
- **SC-008**: System correctly escalates 100% of policy-related requests (no unauthorized automated decisions)
- **SC-009**: PII is never exposed in logs or responses (100% compliance)

## Assumptions

- Students authenticate via existing university SSO before accessing the support agent
- ServiceNow (or equivalent ticketing system) API is available for ticket creation
- University knowledge base content is available and indexed for search
- All external service integrations (ticketing, knowledge base, LLM) are abstracted behind interfaces with mock implementations for demo/testing mode
- Student ID can be obtained from authenticated session context
- Departments have defined SLAs that can be referenced for response time estimates
- v1 scope is English language only; multilingual support deferred to v2
- v1 scope is students only; faculty and staff support deferred to v2 and v3

## Dependencies

- University authentication system (SSO/OAuth)
- Ticketing system API (ServiceNow or equivalent)
- Knowledge base and search infrastructure
- Session storage infrastructure for stateful conversations
- Audit logging infrastructure

## Clarifications

### Session 2026-01-20

- Q: What is the target concurrent user capacity during peak periods? → A: 500 concurrent users (mid-size university peak)
- Q: How should the system behave when SSO authentication is unavailable? → A: Allow read-only KB browsing; block ticket creation until authenticated
- Q: How should intent classification be implemented? → A: LLM-based classification with few-shot prompting (no training data needed)
- Q: Should external integrations support mock mode for demo/testing? → A: Yes, dual-mode with abstracted services and mock implementations
- Q: What format should ticket IDs use? → A: Structured format TKT-{DEPT}-{YYYYMMDD}-{SEQ} (e.g., TKT-IT-20260121-0042)

## Out of Scope (v1)

- Faculty and staff support (v2, v3)
- Multi-language support (v2)
- Proactive notifications ("Your transcript is ready")
- Sentiment-based crisis detection with automatic emergency escalation
- Integration with grant databases or research systems
- Voice/phone channel support
