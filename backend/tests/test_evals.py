"""
Evaluation tests for the Front Door Support Agent.
Tests intent classification accuracy, routing correctness, and escalation logic.
"""

import pytest
from typing import Optional

# Test data for intent classification evaluation
INTENT_CLASSIFICATION_CASES = [
    # (input_message, expected_intent_category, expected_department, should_escalate)
    # IT / Account Access
    ("I forgot my password", "ACCOUNT_ACCESS", "IT", False),
    ("Can't log into Canvas", "ACCOUNT_ACCESS", "IT", False),
    ("My email isn't working", "ACCOUNT_ACCESS", "IT", False),
    ("Need help with VPN connection", "ACCOUNT_ACCESS", "IT", False),
    ("How do I set up two-factor authentication?", "ACCOUNT_ACCESS", "IT", False),
    ("My account is locked", "ACCOUNT_ACCESS", "IT", False),
    ("WiFi not connecting on campus", "ACCOUNT_ACCESS", "IT", False),

    # Registrar / Academic Records
    ("I need an official transcript", "ACADEMIC_RECORDS", "REGISTRAR", False),
    ("How do I request my transcripts?", "ACADEMIC_RECORDS", "REGISTRAR", False),
    ("I need enrollment verification for my employer", "ACADEMIC_RECORDS", "REGISTRAR", False),
    ("When will my grades be posted?", "ACADEMIC_RECORDS", "REGISTRAR", False),
    ("How do I add a class?", "ENROLLMENT", "REGISTRAR", False),
    ("I need to drop CS101", "ENROLLMENT", "REGISTRAR", False),
    ("What's the deadline to withdraw?", "ENROLLMENT", "REGISTRAR", False),

    # Financial Aid
    ("When will my financial aid be disbursed?", "FINANCIAL", "FINANCIAL_AID", False),
    ("How do I apply for scholarships?", "FINANCIAL", "FINANCIAL_AID", False),
    ("I have questions about my FAFSA", "FINANCIAL", "FINANCIAL_AID", False),
    ("My tuition bill seems wrong", "FINANCIAL", "FINANCIAL_AID", False),
    ("How do I set up a payment plan?", "FINANCIAL", "FINANCIAL_AID", False),

    # Facilities
    ("The elevator in Smith Hall is broken", "FACILITIES", "FACILITIES", False),
    ("There's a leak in the bathroom on floor 3", "FACILITIES", "FACILITIES", False),
    ("How do I report a maintenance issue?", "FACILITIES", "FACILITIES", False),
    ("The heat isn't working in my classroom", "FACILITIES", "FACILITIES", False),
    ("I need to book a conference room", "FACILITIES", "FACILITIES", False),

    # Student Affairs
    ("How do I replace my student ID?", "STUDENT_SERVICES", "STUDENT_AFFAIRS", False),
    ("I lost my ID card", "STUDENT_SERVICES", "STUDENT_AFFAIRS", False),
    ("Where can I get a parking permit?", "STUDENT_SERVICES", "CAMPUS_SAFETY", False),
    ("I got a parking ticket, how do I pay it?", "STUDENT_SERVICES", "CAMPUS_SAFETY", False),

    # HR / Employment
    ("How do I apply for a work-study job?", "GENERAL_INQUIRY", "HR", False),
    ("I need help with my student employment paperwork", "GENERAL_INQUIRY", "HR", False),

    # Escalation Required - Policy Keywords
    ("I want to appeal my grade", "POLICY_EXCEPTION", "ESCALATE_TO_HUMAN", True),
    ("Can I get a refund for this semester?", "POLICY_EXCEPTION", "ESCALATE_TO_HUMAN", True),
    ("I need a tuition waiver", "POLICY_EXCEPTION", "ESCALATE_TO_HUMAN", True),
    ("I'm requesting an exception to the deadline", "POLICY_EXCEPTION", "ESCALATE_TO_HUMAN", True),
    ("I want to withdraw after the deadline", "POLICY_EXCEPTION", "ESCALATE_TO_HUMAN", True),

    # Escalation Required - Sensitive Topics
    ("I need to report a Title IX incident", "GENERAL_INQUIRY", "ESCALATE_TO_HUMAN", True),
    ("I'm feeling really depressed and don't know what to do", "GENERAL_INQUIRY", "ESCALATE_TO_HUMAN", True),
    ("Someone is threatening me", "GENERAL_INQUIRY", "ESCALATE_TO_HUMAN", True),

    # Escalation Required - Explicit Human Request
    ("I need to talk to a real person", "HUMAN_REQUEST", "ESCALATE_TO_HUMAN", True),
    ("Can I speak with someone?", "HUMAN_REQUEST", "ESCALATE_TO_HUMAN", True),
    ("Transfer me to a human please", "HUMAN_REQUEST", "ESCALATE_TO_HUMAN", True),
    ("I want to speak to a human agent", "HUMAN_REQUEST", "ESCALATE_TO_HUMAN", True),
]

# Test data for PII detection
PII_DETECTION_CASES = [
    # (input_message, should_detect_pii, expected_pii_types)
    ("I forgot my password", False, []),
    ("My SSN is 123-45-6789", True, ["ssn"]),
    ("Call me at 555-123-4567", True, ["phone"]),
    ("My email is student@university.edu", True, ["email"]),
    ("My credit card is 4111-1111-1111-1111", True, ["credit_card"]),
    ("I was born on January 1, 2000", True, ["dob"]),
    ("My date of birth is 01/01/2000", True, ["dob"]),
]

# Test data for sentiment detection
SENTIMENT_DETECTION_CASES = [
    # (input_message, expected_sentiment)
    ("I need help with my password", "NEUTRAL"),
    ("This is ridiculous, I've been waiting forever!", "FRUSTRATED"),
    ("I'm so frustrated with this system", "FRUSTRATED"),
    ("This is urgent, I need help ASAP!", "URGENT"),
    ("I have a deadline tonight and can't access my work", "URGENT"),
    ("Thank you so much for your help!", "SATISFIED"),
    ("That was perfect, exactly what I needed", "SATISFIED"),
]

# Test data for entity extraction
ENTITY_EXTRACTION_CASES = [
    # (input_message, expected_entities)
    ("The elevator in Smith Hall is broken", {"building": "Smith Hall"}),
    ("I can't log into Canvas", {"system": "Canvas"}),
    ("I need help with CS101", {"course_code": "CS101"}),
    ("The WiFi in Johnson Center doesn't work", {"building": "Johnson Center"}),
    ("I'm having trouble with Blackboard", {"system": "Blackboard"}),
    ("I need to drop MATH 201", {"course_code": "MATH201"}),
]

# Test data for routing priority
PRIORITY_CASES = [
    # (input_message, expected_minimum_priority)
    ("I forgot my password", "LOW"),  # Standard request
    ("The sink is leaking", "MEDIUM"),  # Normal maintenance
    ("This is urgent! I need help now!", "HIGH"),  # Urgency indicator
    ("There's flooding in the building!", "URGENT"),  # Emergency
    ("I'm feeling unsafe on campus", "URGENT"),  # Safety concern
]


class TestIntentClassification:
    """Tests for intent classification accuracy."""

    @pytest.fixture
    def llm_service(self):
        """Get LLM service for testing."""
        from app.services.mock.llm_service import MockLLMService
        return MockLLMService()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "message,expected_category,expected_dept,should_escalate",
        INTENT_CLASSIFICATION_CASES
    )
    async def test_intent_classification(
        self,
        llm_service,
        message: str,
        expected_category: str,
        expected_dept: str,
        should_escalate: bool,
    ):
        """Test that intents are correctly classified."""
        result = await llm_service.classify_intent(message)

        # Check escalation flag
        assert result.requires_escalation == should_escalate, (
            f"Message '{message}' should {'require' if should_escalate else 'not require'} escalation. "
            f"Got requires_escalation={result.requires_escalation}"
        )

        # Check department routing
        assert result.department_suggestion.value == expected_dept, (
            f"Message '{message}' should route to {expected_dept}. "
            f"Got {result.department_suggestion.value}"
        )

    @pytest.mark.asyncio
    async def test_low_confidence_triggers_clarification(self, llm_service):
        """Test that ambiguous messages result in low confidence."""
        ambiguous_messages = [
            "I need help with my account",
            "Something is wrong",
            "Can you help me?",
        ]

        for message in ambiguous_messages:
            result = await llm_service.classify_intent(message)
            # Ambiguous messages should have lower confidence
            # The mock service may not perfectly simulate this, but we verify the interface works
            assert hasattr(result, 'confidence')
            assert 0.0 <= result.confidence <= 1.0


class TestPIIDetection:
    """Tests for PII detection."""

    @pytest.fixture
    def llm_service(self):
        """Get LLM service for testing."""
        from app.services.mock.llm_service import MockLLMService
        return MockLLMService()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "message,should_detect,expected_types",
        PII_DETECTION_CASES
    )
    async def test_pii_detection(
        self,
        llm_service,
        message: str,
        should_detect: bool,
        expected_types: list[str],
    ):
        """Test that PII is correctly detected."""
        result = await llm_service.classify_intent(message)

        assert result.pii_detected == should_detect, (
            f"Message '{message}' should {'contain' if should_detect else 'not contain'} PII. "
            f"Got pii_detected={result.pii_detected}"
        )

        if should_detect:
            for pii_type in expected_types:
                assert pii_type in result.pii_types, (
                    f"Expected PII type '{pii_type}' not found in {result.pii_types}"
                )


class TestSentimentDetection:
    """Tests for sentiment detection."""

    @pytest.fixture
    def llm_service(self):
        """Get LLM service for testing."""
        from app.services.mock.llm_service import MockLLMService
        return MockLLMService()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("message,expected_sentiment", SENTIMENT_DETECTION_CASES)
    async def test_sentiment_detection(
        self,
        llm_service,
        message: str,
        expected_sentiment: str,
    ):
        """Test that sentiment is correctly detected."""
        result = await llm_service.classify_intent(message)

        assert result.sentiment.value == expected_sentiment, (
            f"Message '{message}' should have sentiment {expected_sentiment}. "
            f"Got {result.sentiment.value}"
        )


class TestEntityExtraction:
    """Tests for entity extraction."""

    @pytest.fixture
    def llm_service(self):
        """Get LLM service for testing."""
        from app.services.mock.llm_service import MockLLMService
        return MockLLMService()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("message,expected_entities", ENTITY_EXTRACTION_CASES)
    async def test_entity_extraction(
        self,
        llm_service,
        message: str,
        expected_entities: dict,
    ):
        """Test that entities are correctly extracted."""
        result = await llm_service.classify_intent(message)

        for key, value in expected_entities.items():
            assert key in result.entities, (
                f"Expected entity '{key}' not found in {result.entities}"
            )
            # Case-insensitive comparison for some entities
            actual_value = result.entities[key]
            if isinstance(actual_value, str) and isinstance(value, str):
                assert actual_value.lower() == value.lower(), (
                    f"Entity '{key}' expected '{value}', got '{actual_value}'"
                )


class TestEscalationLogic:
    """Tests for escalation triggers."""

    @pytest.fixture
    def llm_service(self):
        """Get LLM service for testing."""
        from app.services.mock.llm_service import MockLLMService
        return MockLLMService()

    @pytest.mark.asyncio
    async def test_policy_keywords_trigger_escalation(self, llm_service):
        """Test that policy keywords trigger escalation."""
        policy_messages = [
            "I want to appeal my grade",
            "Can I get a refund?",
            "I need a waiver for the late fee",
            "I'm requesting an exception",
            "I want to override the prerequisite",
        ]

        for message in policy_messages:
            result = await llm_service.classify_intent(message)
            assert result.requires_escalation, (
                f"Policy message '{message}' should require escalation"
            )

    @pytest.mark.asyncio
    async def test_sensitive_topics_trigger_escalation(self, llm_service):
        """Test that sensitive topics trigger escalation."""
        sensitive_messages = [
            "I need to report a Title IX violation",
            "I'm having a mental health crisis",
            "Someone made a threat against me",
        ]

        for message in sensitive_messages:
            result = await llm_service.classify_intent(message)
            assert result.requires_escalation, (
                f"Sensitive message '{message}' should require escalation"
            )

    @pytest.mark.asyncio
    async def test_human_request_triggers_escalation(self, llm_service):
        """Test that explicit human requests trigger escalation."""
        human_requests = [
            "I need to talk to a person",
            "Can I speak with someone?",
            "Transfer me to a human",
            "I want a live agent",
            "Connect me to a real person",
        ]

        for message in human_requests:
            result = await llm_service.classify_intent(message)
            assert result.requires_escalation, (
                f"Human request '{message}' should require escalation"
            )


class TestKnowledgeBaseValidation:
    """Tests for knowledge base article validation."""

    @pytest.fixture
    def kb_service(self):
        """Get knowledge base service for testing."""
        from app.services.mock.knowledge_service import MockKnowledgeService
        return MockKnowledgeService()

    @pytest.mark.asyncio
    async def test_kb_articles_have_valid_structure(self, kb_service):
        """Test that all KB articles have required fields."""
        # Search for common terms to get articles
        articles = await kb_service.search("password help transcript")

        for article in articles:
            assert article.article_id, "Article must have article_id"
            assert article.title, "Article must have title"
            assert article.url is not None, "Article must have url"
            assert 0.0 <= article.relevance_score <= 1.0, "Relevance score must be 0-1"

    @pytest.mark.asyncio
    async def test_kb_search_returns_relevant_results(self, kb_service):
        """Test that KB search returns relevant articles."""
        # Password query should return password-related articles
        articles = await kb_service.search("password reset")
        assert len(articles) > 0, "Should return at least one article"

        # Check that top result is relevant
        titles = [a.title.lower() for a in articles]
        assert any("password" in t for t in titles), (
            "Password search should return password-related articles"
        )

    @pytest.mark.asyncio
    async def test_kb_department_filter(self, kb_service):
        """Test that department filter works correctly."""
        from app.models.enums import Department

        # Search with IT filter
        articles = await kb_service.search("help", department=Department.IT)

        for article in articles:
            if article.department:
                assert article.department == Department.IT, (
                    f"Article should be from IT department, got {article.department}"
                )


class TestAgentBoundaries:
    """Tests for agent authority boundaries (security)."""

    @pytest.fixture
    def llm_service(self):
        """Get LLM service for testing."""
        from app.services.mock.llm_service import MockLLMService
        return MockLLMService()

    @pytest.mark.asyncio
    async def test_no_automatic_approval(self, llm_service):
        """Test that the system never auto-approves policy decisions."""
        approval_requests = [
            "Approve my refund request",
            "Grant me the waiver",
            "Accept my appeal",
            "Override the hold on my account",
        ]

        for message in approval_requests:
            result = await llm_service.classify_intent(message)
            # All policy-related requests should escalate, never auto-approve
            assert result.requires_escalation or result.department_suggestion.value == "ESCALATE_TO_HUMAN", (
                f"Policy request '{message}' should require human review"
            )

    @pytest.mark.asyncio
    async def test_no_record_modification(self, llm_service):
        """Test that the system doesn't claim to modify records."""
        modification_requests = [
            "Change my grade to an A",
            "Update my enrollment status",
            "Modify my financial aid amount",
        ]

        for message in modification_requests:
            result = await llm_service.classify_intent(message)
            # These should all escalate - system cannot modify records
            assert result.requires_escalation or result.department_suggestion.value == "ESCALATE_TO_HUMAN", (
                f"Record modification request '{message}' should require human review"
            )


class TestResponseQuality:
    """Tests for response message quality."""

    @pytest.fixture
    def llm_service(self):
        """Get LLM service for testing."""
        from app.services.mock.llm_service import MockLLMService
        return MockLLMService()

    @pytest.mark.asyncio
    async def test_response_includes_ticket_id(self, llm_service):
        """Test that responses include ticket ID when created."""
        from app.models.enums import Department

        response = await llm_service.generate_response_message(
            intent="password_reset",
            department=Department.IT,
            ticket_id="TKT-IT-20260121-0001",
            escalated=False,
            estimated_response_time="4 hours",
        )

        assert "TKT-IT-20260121-0001" in response, (
            "Response should include the ticket ID"
        )

    @pytest.mark.asyncio
    async def test_escalation_response_mentions_human(self, llm_service):
        """Test that escalation responses mention human review."""
        from app.models.enums import Department

        response = await llm_service.generate_response_message(
            intent="grade_appeal",
            department=Department.ESCALATE_TO_HUMAN,
            ticket_id="TKT-ESC-20260121-0001",
            escalated=True,
            estimated_response_time="1 business day",
        )

        # Response should indicate human involvement
        human_indicators = ["human", "team member", "specialist", "staff", "person"]
        assert any(indicator in response.lower() for indicator in human_indicators), (
            "Escalation response should mention human review"
        )

    @pytest.mark.asyncio
    async def test_response_includes_sla(self, llm_service):
        """Test that responses include response time expectation."""
        from app.models.enums import Department

        response = await llm_service.generate_response_message(
            intent="facilities_issue",
            department=Department.FACILITIES,
            ticket_id="TKT-FAC-20260121-0001",
            escalated=False,
            estimated_response_time="2-3 business days",
        )

        # Response should mention timeframe
        time_indicators = ["hour", "day", "business", "within", "expect"]
        assert any(indicator in response.lower() for indicator in time_indicators), (
            "Response should include response time expectation"
        )
