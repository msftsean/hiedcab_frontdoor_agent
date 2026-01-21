<!--
SYNC IMPACT REPORT
==================
Version change: N/A → 1.0.0 (initial ratification)
Modified principles: N/A (new constitution)
Added sections:
  - Core Principles (7 principles)
  - Security & Compliance Constraints
  - Development Workflow
  - Governance
Removed sections: N/A
Templates requiring updates:
  - .specify/templates/plan-template.md: ✅ Compatible (Constitution Check section exists)
  - .specify/templates/spec-template.md: ✅ Compatible (no changes required)
  - .specify/templates/tasks-template.md: ✅ Compatible (no changes required)
Follow-up TODOs: None
-->

# Front Door Support Agent Constitution

## Core Principles

### I. Bounded Agent Authority (NON-NEGOTIABLE)

Each agent component MUST have explicitly defined boundaries enforced architecturally:
- Agents MUST NOT have access to methods, services, or APIs that exceed their designated authority
- QueryAgent: Intent detection and entity extraction ONLY - no routing decisions, no ticket creation
- RouterAgent: Routing decisions ONLY - no intent detection, no ticket creation, no user communication
- ActionAgent: Ticket creation and knowledge retrieval ONLY - no approval methods, no record modification
- The absence of unauthorized capabilities MUST be enforced at the code level (methods simply do not exist)

**Rationale**: Architectural boundaries prevent scope creep and unauthorized actions. If a method doesn't exist, it cannot be called—this is safer than runtime permission checks.

### II. Human Escalation for Policy Decisions (NON-NEGOTIABLE)

The system MUST escalate to human reviewers for any decision requiring judgment, policy interpretation, or exception handling:
- Confidence score below 0.70 threshold
- Policy keywords detected (appeal, waiver, exception, override, refund, withdrawal deadline)
- Sensitive topics (Title IX, mental health, threats, discrimination)
- Multi-department coordination required
- User explicitly requests human contact
- Ambiguity unresolved after 3 clarification attempts

**Rationale**: Automated systems MUST NOT make decisions that affect student rights, finances, or academic standing. Human judgment is required for policy exceptions.

### III. Privacy-First Data Handling (NON-NEGOTIABLE)

All student data MUST be handled with privacy as the default:
- Student IDs MUST be hashed before storage in session and audit logs
- Raw query text containing PII MUST NOT be persisted beyond immediate processing
- Audit logs MUST capture intent and routing decisions without exposing sensitive content
- PII detection MUST flag queries for secure handling before any logging occurs
- Session history MUST store only PII-safe context (intents, ticket IDs, timestamps)

**Rationale**: FERPA compliance and student trust require that personal information is protected by design, not by policy alone.

### IV. Stateful Context Preservation

The system MUST maintain conversation context across multi-turn interactions:
- Session state MUST persist student context, conversation history, and ticket references
- Follow-up queries ("What's the status of my ticket?") MUST resolve without re-authentication
- Session data MUST be retained for 90 days before anonymization for analytics
- Graceful degradation MUST occur if session storage is unavailable (inform user, continue stateless)

**Rationale**: Students should not need to re-explain their situation. Stateful design enables natural conversation and reduces frustration.

### V. Test-First Development

All agent behaviors MUST be validated through tests written before implementation:
- Acceptance scenarios from the spec MUST be converted to executable tests
- Intent detection MUST be tested against the defined query-to-intent mappings
- Escalation triggers MUST be tested to ensure 100% of policy queries escalate
- Boundary violations MUST be tested (attempting unauthorized actions should fail)

**Rationale**: Agent systems have high stakes for incorrect behavior. Test-first ensures behaviors are verified, not assumed.

### VI. Accessibility as Requirement

The user interface MUST meet accessibility standards as functional requirements, not afterthoughts:
- WCAG AA compliance MUST be achieved; AAA for high-contrast mode
- All interactive elements MUST be keyboard navigable
- Screen reader compatibility MUST be validated
- Mobile responsiveness MUST be tested on actual devices

**Rationale**: University services must be accessible to all students. Accessibility is a legal requirement (ADA/Section 508) and an ethical imperative.

### VII. Graceful Degradation

The system MUST continue providing value when external dependencies fail:
- If ticketing system is unavailable: Log request for retry, inform user, provide KB articles
- If knowledge base is unavailable: Create ticket, inform user help articles temporarily unavailable
- If LLM service is unavailable: Provide fallback routing based on keyword matching, escalate to human
- All degradation states MUST be logged for operational visibility

**Rationale**: 24/7 availability is a core promise. Partial functionality is better than complete failure.

## Security & Compliance Constraints

### Data Access Boundaries
- System MUST NOT access FERPA-protected student records beyond routing context
- System MUST NOT store financial data (account numbers, SSN, payment info)
- System MUST NOT retain health information beyond routing to appropriate support

### Integration Security
- All external API calls MUST use authenticated, encrypted connections
- API credentials MUST NOT be stored in code or logs
- Rate limiting MUST be implemented on all endpoints

### Audit Requirements
- All routing decisions MUST be logged with timestamp, intent, department, and escalation status
- Audit logs MUST be immutable (append-only)
- Logs MUST be retained per university data retention policy (minimum 7 years for FERPA)

## Development Workflow

### Code Review Requirements
- All changes MUST be reviewed before merge
- Reviewer MUST verify Constitution compliance (boundary enforcement, escalation triggers, privacy handling)
- Security-sensitive changes MUST have security-focused review

### Quality Gates
- All tests MUST pass before merge
- Code coverage MUST not decrease
- Accessibility tests MUST pass for UI changes
- Performance benchmarks MUST meet <30 second response time requirement

### Documentation Standards
- API contracts MUST be documented in OpenAPI format
- Agent boundaries MUST be documented in code comments
- Escalation rules MUST be documented and version-controlled

## Governance

This Constitution establishes non-negotiable principles for the Front Door Support Agent. All development decisions MUST comply with these principles.

### Amendment Process
1. Propose amendment with rationale and impact analysis
2. Review against existing principles for conflicts
3. Update version number per semantic versioning:
   - MAJOR: Principle removal or fundamental redefinition
   - MINOR: New principle or material expansion of existing guidance
   - PATCH: Clarifications, wording improvements, non-semantic changes
4. Update dependent templates if affected
5. Document migration plan for existing code if breaking change

### Compliance Verification
- All pull requests MUST include Constitution compliance checklist
- Quarterly review of system behavior against principles
- Incident post-mortems MUST assess Constitution adherence

### Conflict Resolution
- Constitution principles take precedence over convenience or speed
- When principles conflict, prioritize: Privacy > Security > Human Escalation > User Experience
- Document conflicts and resolutions in decision log

**Version**: 1.0.0 | **Ratified**: 2026-01-20 | **Last Amended**: 2026-01-20
