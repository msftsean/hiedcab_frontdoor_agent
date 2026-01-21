"""
GPT-4o Model Evaluation Tests for the Front Door Support Agent.

These tests evaluate the Azure OpenAI GPT-4o model's performance on:
- Intent classification accuracy
- Department routing correctness
- Escalation detection for policy keywords and sensitive topics
- PII detection
- Entity extraction
- Sentiment analysis

Tests are skipped if Azure OpenAI credentials are not configured.

NOTE: These tests require real Azure OpenAI credentials from the .env file.
The conftest.py fixture is configured to NOT override these credentials
for this specific test file.
"""

import os
import pytest
from typing import Optional

# Load environment variables from .env file BEFORE the skipif check
from dotenv import load_dotenv
load_dotenv()

# Skip all tests if Azure OpenAI is not configured
pytestmark = pytest.mark.skipif(
    not os.environ.get("AZURE_OPENAI_ENDPOINT") or not os.environ.get("AZURE_OPENAI_API_KEY"),
    reason="Azure OpenAI credentials not configured"
)


# =============================================================================
# Test Data
# =============================================================================

# Intent classification test cases
# (message, expected_intent_category, expected_department, should_escalate)
# Note: expected_intent_category can be a list to allow multiple acceptable categories
# since GPT-4o may reasonably classify queries differently (e.g., "status check" vs "academic records")
INTENT_CLASSIFICATION_CASES = [
    # IT / Account Access
    ("I forgot my password", "ACCOUNT_ACCESS", "IT", False),
    ("Can't log into Canvas", "ACCOUNT_ACCESS", "IT", False),
    ("My email isn't working", "ACCOUNT_ACCESS", "IT", False),
    ("Need help with VPN connection", "ACCOUNT_ACCESS", "IT", False),
    ("How do I set up two-factor authentication?", ["ACCOUNT_ACCESS", "GENERAL_INQUIRY"], "IT", False),
    ("My account is locked", "ACCOUNT_ACCESS", "IT", False),
    ("WiFi not connecting on campus", "ACCOUNT_ACCESS", "IT", False),

    # Registrar / Academic Records
    ("I need an official transcript", "ACADEMIC_RECORDS", "REGISTRAR", False),
    ("How do I request my transcripts?", "ACADEMIC_RECORDS", "REGISTRAR", False),
    ("I need enrollment verification for my employer", "ACADEMIC_RECORDS", "REGISTRAR", False),
    ("When will my grades be posted?", ["ACADEMIC_RECORDS", "STATUS_CHECK"], "REGISTRAR", False),
    ("How do I add a class?", "ENROLLMENT", "REGISTRAR", False),
    ("I need to drop CS101", "ENROLLMENT", "REGISTRAR", False),
    ("What's the deadline to withdraw?", ["ENROLLMENT", "GENERAL_INQUIRY"], "REGISTRAR", False),

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
    ("How do I replace my student ID?", ["STUDENT_SERVICES", "GENERAL_INQUIRY"], "STUDENT_AFFAIRS", False),
    ("I lost my ID card", ["STUDENT_SERVICES", "GENERAL_INQUIRY"], "STUDENT_AFFAIRS", False),
    ("Where can I get a parking permit?", "STUDENT_SERVICES", ["CAMPUS_SAFETY", "STUDENT_AFFAIRS"], False),
    ("I got a parking ticket, how do I pay it?", "STUDENT_SERVICES", ["CAMPUS_SAFETY", "STUDENT_AFFAIRS"], False),

    # HR / Employment
    ("How do I apply for a work-study job?", "GENERAL_INQUIRY", "HR", False),
    ("I need help with my student employment paperwork", "GENERAL_INQUIRY", "HR", False),

    # Escalation Required - Policy Keywords
    # GPT-4o may classify these as POLICY_EXCEPTION, HUMAN_REQUEST, or even ENROLLMENT
    # The key test is that they all escalate and route to ESCALATE_TO_HUMAN
    ("I want to appeal my grade", ["POLICY_EXCEPTION", "HUMAN_REQUEST"], "ESCALATE_TO_HUMAN", True),
    ("Can I get a refund for this semester?", ["POLICY_EXCEPTION", "HUMAN_REQUEST", "FINANCIAL"], "ESCALATE_TO_HUMAN", True),
    ("I need a tuition waiver", ["POLICY_EXCEPTION", "HUMAN_REQUEST", "FINANCIAL"], "ESCALATE_TO_HUMAN", True),
    ("I'm requesting an exception to the deadline", ["POLICY_EXCEPTION", "HUMAN_REQUEST", "GENERAL_INQUIRY"], "ESCALATE_TO_HUMAN", True),
    ("I want to withdraw after the deadline", ["POLICY_EXCEPTION", "HUMAN_REQUEST", "ENROLLMENT"], "ESCALATE_TO_HUMAN", True),

    # Escalation Required - Sensitive Topics
    # GPT-4o correctly identifies these as needing human intervention (HUMAN_REQUEST)
    # Threats may reasonably route to CAMPUS_SAFETY instead of ESCALATE_TO_HUMAN
    ("I need to report a Title IX incident", ["GENERAL_INQUIRY", "HUMAN_REQUEST"], "ESCALATE_TO_HUMAN", True),
    ("I'm feeling really depressed and don't know what to do", ["GENERAL_INQUIRY", "HUMAN_REQUEST"], "ESCALATE_TO_HUMAN", True),
    ("Someone is threatening me", ["GENERAL_INQUIRY", "HUMAN_REQUEST"], ["ESCALATE_TO_HUMAN", "CAMPUS_SAFETY"], True),

    # Escalation Required - Explicit Human Request
    ("I need to talk to a real person", "HUMAN_REQUEST", "ESCALATE_TO_HUMAN", True),
    ("Can I speak with someone?", "HUMAN_REQUEST", "ESCALATE_TO_HUMAN", True),
    ("Transfer me to a human please", "HUMAN_REQUEST", "ESCALATE_TO_HUMAN", True),
]

# PII detection test cases
PII_DETECTION_CASES = [
    ("I forgot my password", False, []),
    ("My SSN is 123-45-6789", True, ["ssn"]),
    ("Call me at 555-123-4567", True, ["phone"]),
    ("My email is student@university.edu", True, ["email"]),
    ("My credit card is 4111-1111-1111-1111", True, ["credit_card"]),
    ("I was born on January 1, 2000", True, ["dob"]),
    ("My social security number is 987-65-4321", True, ["ssn"]),
]

# Sentiment detection test cases
SENTIMENT_DETECTION_CASES = [
    ("I need help with my password", "NEUTRAL"),
    ("This is ridiculous, I've been waiting forever!", "FRUSTRATED"),
    ("I'm so frustrated with this system", "FRUSTRATED"),
    ("This is urgent, I need help ASAP!", "URGENT"),
    ("I have a deadline tonight and can't access my work", "URGENT"),
    ("Thank you so much for your help!", "SATISFIED"),
    ("That was perfect, exactly what I needed", "SATISFIED"),
]

# Entity extraction test cases
ENTITY_EXTRACTION_CASES = [
    ("The elevator in Smith Hall is broken", {"building": "Smith Hall"}),
    ("I can't log into Canvas", {"system": "Canvas"}),
    ("The WiFi in the Engineering Building isn't working", {"building": "Engineering Building"}),
    ("I need help with my CS 101 class", {"course_code": "CS 101"}),
    ("I have a deadline on December 15th", {"date": "December 15th"}),
    ("I need my transcript by next Friday", {"date": "next Friday"}),
]

# Urgency indicator test cases
URGENCY_INDICATOR_CASES = [
    ("I need help ASAP", ["asap"]),
    ("This is urgent, please help", ["urgent"]),
    ("I have a deadline today", ["deadline", "today"]),
    ("I need this resolved tonight", ["tonight"]),
    ("It's an emergency", ["emergency"]),
    ("I need help with my password", []),
]


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def gpt4o_service():
    """Create Azure OpenAI LLM service instance."""
    from app.services.azure.llm_service import AzureOpenAILLMService

    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY", "")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-05-01-preview")

    service = AzureOpenAILLMService(
        endpoint=endpoint,
        api_key=api_key,
        deployment=deployment,
        api_version=api_version,
    )
    yield service


@pytest.fixture
def settings():
    """Create settings for router agent."""
    from app.core.config import Settings
    return Settings()


@pytest.fixture
def router_agent(settings):
    """Create router agent instance."""
    from app.agents.router_agent import RouterAgent
    return RouterAgent(settings)


# =============================================================================
# Intent Classification Tests
# =============================================================================

class TestGPT4oIntentClassification:
    """Evaluate GPT-4o intent classification accuracy."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("message,expected_category,expected_dept,should_escalate", INTENT_CLASSIFICATION_CASES)
    async def test_intent_classification(
        self,
        gpt4o_service,
        message: str,
        expected_category,
        expected_dept,
        should_escalate: bool,
    ):
        """Test that GPT-4o correctly classifies intent and routes to department."""
        result = await gpt4o_service.classify_intent(message)

        # Check intent category (allow list for ambiguous cases)
        if isinstance(expected_category, list):
            assert result.intent_category.value in expected_category, (
                f"Message '{message}' - expected category in {expected_category}, "
                f"got {result.intent_category.value}"
            )
        else:
            assert result.intent_category.value == expected_category, (
                f"Message '{message}' - expected category {expected_category}, "
                f"got {result.intent_category.value}"
            )

        # Check department (allow list for ambiguous cases)
        if isinstance(expected_dept, list):
            assert result.department_suggestion.value in expected_dept, (
                f"Message '{message}' - expected dept in {expected_dept}, "
                f"got {result.department_suggestion.value}"
            )
        else:
            assert result.department_suggestion.value == expected_dept, (
                f"Message '{message}' - expected dept {expected_dept}, "
                f"got {result.department_suggestion.value}"
            )

        # Check escalation
        assert result.requires_escalation == should_escalate, (
            f"Message '{message}' - expected escalation={should_escalate}, "
            f"got {result.requires_escalation}"
        )

    @pytest.mark.asyncio
    async def test_confidence_score_range(self, gpt4o_service):
        """Test that confidence scores are in valid range [0, 1]."""
        messages = [
            "I forgot my password",
            "The elevator is broken",
            "I want to appeal my grade",
            "asdfghjkl random text",
        ]

        for message in messages:
            result = await gpt4o_service.classify_intent(message)
            assert 0.0 <= result.confidence <= 1.0, (
                f"Confidence {result.confidence} out of range for '{message}'"
            )

    @pytest.mark.asyncio
    async def test_low_confidence_for_ambiguous(self, gpt4o_service):
        """Test that ambiguous messages have lower confidence."""
        ambiguous_messages = [
            "help",
            "problem",
            "question",
            "asdfghjkl",
        ]

        for message in ambiguous_messages:
            result = await gpt4o_service.classify_intent(message)
            # Ambiguous messages should generally have confidence < 0.9
            assert result.confidence < 0.95, (
                f"Ambiguous message '{message}' should have lower confidence, "
                f"got {result.confidence}"
            )


# =============================================================================
# Escalation Detection Tests
# =============================================================================

class TestGPT4oEscalationDetection:
    """Evaluate GPT-4o escalation detection accuracy."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("message,expected_depts", [
        ("I want to appeal my grade", ["ESCALATE_TO_HUMAN"]),
        ("Can I get a refund?", ["ESCALATE_TO_HUMAN"]),
        ("I need a tuition waiver", ["ESCALATE_TO_HUMAN"]),
        ("I'm requesting an exception", ["ESCALATE_TO_HUMAN"]),
        ("Can you override this requirement?", ["ESCALATE_TO_HUMAN"]),
        # Late withdrawal may route to REGISTRAR or ESCALATE_TO_HUMAN depending on LLM interpretation
        ("I want to withdraw after the deadline", ["ESCALATE_TO_HUMAN", "REGISTRAR"]),
    ])
    async def test_policy_keyword_escalation(self, gpt4o_service, message: str, expected_depts: list):
        """Test escalation for policy keywords."""
        result = await gpt4o_service.classify_intent(message)
        assert result.requires_escalation is True, (
            f"Policy message '{message}' should require escalation"
        )
        assert result.department_suggestion.value in expected_depts, (
            f"Policy message '{message}' should route to one of {expected_depts}, "
            f"got {result.department_suggestion.value}"
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize("message", [
        "I need to report a Title IX incident",
        "I'm being sexually harassed",
        "I'm feeling suicidal",
        "I'm having a mental health crisis",
        "Someone threatened to hurt me",
        "There's been a violent incident",
    ])
    async def test_sensitive_topic_escalation(self, gpt4o_service, message: str):
        """Test escalation for sensitive topics."""
        result = await gpt4o_service.classify_intent(message)
        assert result.requires_escalation is True, (
            f"Sensitive message '{message}' should require escalation"
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize("message", [
        "I want to talk to a real person",
        "Can I speak with someone?",
        "Transfer me to a human",
        "I need to speak with an agent",
        "Let me talk to a person",
        "Human please",
    ])
    async def test_explicit_human_request_escalation(self, gpt4o_service, message: str):
        """Test escalation for explicit human requests."""
        result = await gpt4o_service.classify_intent(message)
        assert result.requires_escalation is True, (
            f"Human request '{message}' should require escalation"
        )
        assert result.department_suggestion.value == "ESCALATE_TO_HUMAN"


# =============================================================================
# PII Detection Tests
# =============================================================================

class TestGPT4oPIIDetection:
    """Evaluate GPT-4o PII detection accuracy."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("message,should_detect,expected_types", PII_DETECTION_CASES)
    async def test_pii_detection(
        self,
        gpt4o_service,
        message: str,
        should_detect: bool,
        expected_types: list,
    ):
        """Test PII detection accuracy."""
        result = await gpt4o_service.classify_intent(message)

        assert result.pii_detected == should_detect, (
            f"Message '{message}' - expected pii_detected={should_detect}, "
            f"got {result.pii_detected}"
        )

        if expected_types:
            for pii_type in expected_types:
                assert pii_type in result.pii_types, (
                    f"Message '{message}' should detect PII type '{pii_type}', "
                    f"got {result.pii_types}"
                )

    @pytest.mark.asyncio
    async def test_no_false_positive_pii(self, gpt4o_service):
        """Test that normal messages don't trigger false PII detection."""
        safe_messages = [
            "I forgot my password",
            "The elevator is broken",
            "How do I add a class?",
            "I need a transcript",
            "What are the library hours?",
        ]

        for message in safe_messages:
            result = await gpt4o_service.classify_intent(message)
            assert result.pii_detected is False, (
                f"Safe message '{message}' should not detect PII"
            )


# =============================================================================
# Sentiment Detection Tests
# =============================================================================

class TestGPT4oSentimentDetection:
    """Evaluate GPT-4o sentiment detection accuracy."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("message,expected_sentiment", SENTIMENT_DETECTION_CASES)
    async def test_sentiment_detection(
        self,
        gpt4o_service,
        message: str,
        expected_sentiment: str,
    ):
        """Test sentiment detection accuracy."""
        result = await gpt4o_service.classify_intent(message)

        assert result.sentiment.value == expected_sentiment, (
            f"Message '{message}' - expected sentiment {expected_sentiment}, "
            f"got {result.sentiment.value}"
        )


# =============================================================================
# Entity Extraction Tests
# =============================================================================

class TestGPT4oEntityExtraction:
    """Evaluate GPT-4o entity extraction accuracy."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("message,expected_entities", ENTITY_EXTRACTION_CASES)
    async def test_entity_extraction(
        self,
        gpt4o_service,
        message: str,
        expected_entities: dict,
    ):
        """Test entity extraction accuracy."""
        result = await gpt4o_service.classify_intent(message)

        for entity_type, expected_value in expected_entities.items():
            assert entity_type in result.entities, (
                f"Message '{message}' should extract entity '{entity_type}'"
            )
            # Check if the expected value is contained in the extracted value
            # (to allow for slight variations in extraction)
            extracted = result.entities.get(entity_type, "")
            assert expected_value.lower() in extracted.lower(), (
                f"Message '{message}' - entity '{entity_type}' expected to contain "
                f"'{expected_value}', got '{extracted}'"
            )


# =============================================================================
# Urgency Detection Tests
# =============================================================================

class TestGPT4oUrgencyDetection:
    """Evaluate GPT-4o urgency indicator detection."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("message,expected_indicators", URGENCY_INDICATOR_CASES)
    async def test_urgency_indicator_detection(
        self,
        gpt4o_service,
        message: str,
        expected_indicators: list,
    ):
        """Test urgency indicator detection."""
        result = await gpt4o_service.classify_intent(message)

        if expected_indicators:
            assert len(result.urgency_indicators) > 0, (
                f"Message '{message}' should detect urgency indicators"
            )
            for indicator in expected_indicators:
                found = any(indicator.lower() in ind.lower() for ind in result.urgency_indicators)
                assert found, (
                    f"Message '{message}' should detect urgency indicator '{indicator}', "
                    f"got {result.urgency_indicators}"
                )
        else:
            # Empty expected means no urgency indicators should be detected
            assert len(result.urgency_indicators) == 0, (
                f"Message '{message}' should not detect urgency indicators, "
                f"got {result.urgency_indicators}"
            )


# =============================================================================
# Response Generation Tests
# =============================================================================

class TestGPT4oResponseGeneration:
    """Evaluate GPT-4o response generation quality."""

    @pytest.mark.asyncio
    async def test_clarification_question_generation(self, gpt4o_service):
        """Test clarification question generation."""
        message = "I have a problem"
        possible_intents = ["password_reset", "facilities_issue", "general_question"]

        clarification = await gpt4o_service.generate_clarification_question(
            message=message,
            possible_intents=possible_intents,
        )

        assert len(clarification) > 0, "Clarification should not be empty"
        assert len(clarification) < 500, "Clarification should be concise"
        # Should be asking a question
        assert "?" in clarification, "Clarification should include a question"

    @pytest.mark.asyncio
    async def test_response_message_generation(self, gpt4o_service):
        """Test response message generation."""
        from app.models.enums import Department

        response = await gpt4o_service.generate_response_message(
            intent="password_reset",
            department=Department.IT,
            ticket_id="TKT-IT-20240115-0001",
            escalated=False,
            estimated_response_time="within 4 hours",
            original_message="I forgot my password",
            knowledge_articles=[],
            kb_article_contents=[
                {
                    "title": "Password Reset Guide",
                    "content": "To reset your password, visit the IT portal at it.university.edu/password-reset and follow the instructions."
                }
            ],
        )

        assert len(response) > 0, "Response should not be empty"
        assert len(response) < 2000, "Response should be reasonably concise"

    @pytest.mark.asyncio
    async def test_escalation_response_message(self, gpt4o_service):
        """Test response message for escalated tickets."""
        from app.models.enums import Department

        response = await gpt4o_service.generate_response_message(
            intent="grade_appeal",
            department=Department.ESCALATE_TO_HUMAN,
            ticket_id="TKT-REG-20240115-0001",
            escalated=True,
            estimated_response_time="within 24 hours",
            original_message="I want to appeal my grade",
        )

        assert len(response) > 0, "Response should not be empty"
        # Should mention human/staff follow-up
        response_lower = response.lower()
        assert any(word in response_lower for word in ["human", "staff", "team", "person", "someone"]), (
            "Escalation response should mention human follow-up"
        )


# =============================================================================
# End-to-End Pipeline Tests
# =============================================================================

class TestGPT4oEndToEndPipeline:
    """Test complete agent pipeline with GPT-4o."""

    @pytest.mark.asyncio
    async def test_full_classification_and_routing(self, gpt4o_service, router_agent):
        """Test full classification and routing pipeline."""
        test_cases = [
            ("I forgot my password", "IT", False),
            ("The elevator is broken", "FACILITIES", False),
            ("I want to appeal my grade", "ESCALATE_TO_HUMAN", True),
        ]

        for message, expected_dept, expected_escalation in test_cases:
            # Step 1: Classify with GPT-4o
            query_result = await gpt4o_service.classify_intent(message)

            # Step 2: Route
            routing_decision = router_agent.route(query_result)

            # Verify routing
            assert routing_decision.department.value == expected_dept, (
                f"Message '{message}' should route to {expected_dept}, "
                f"got {routing_decision.department.value}"
            )
            assert routing_decision.escalate_to_human == expected_escalation, (
                f"Message '{message}' escalation mismatch"
            )

    @pytest.mark.asyncio
    async def test_conversation_context(self, gpt4o_service):
        """Test that conversation history affects classification."""
        # First message
        result1 = await gpt4o_service.classify_intent("I have a problem")

        # Follow-up with context
        history = [
            {"role": "user", "content": "I have a problem"},
            {"role": "assistant", "content": "I'd be happy to help. What kind of problem are you experiencing?"},
        ]

        result2 = await gpt4o_service.classify_intent(
            "It's with my Canvas account",
            conversation_history=history,
        )

        # With context about Canvas, should route to IT
        assert result2.department_suggestion.value == "IT", (
            "With Canvas context, should route to IT"
        )


# =============================================================================
# Performance Tests
# =============================================================================

class TestGPT4oPerformance:
    """Test GPT-4o response time and reliability."""

    @pytest.mark.asyncio
    async def test_classification_response_time(self, gpt4o_service):
        """Test that classification completes within acceptable time."""
        import time

        start = time.time()
        await gpt4o_service.classify_intent("I forgot my password")
        elapsed = time.time() - start

        # Classification should complete within 10 seconds
        assert elapsed < 10, f"Classification took {elapsed:.2f}s, expected < 10s"

    @pytest.mark.asyncio
    async def test_health_check(self, gpt4o_service):
        """Test health check endpoint."""
        healthy, latency_ms, error = await gpt4o_service.health_check()

        assert healthy is True, f"Health check failed: {error}"
        assert latency_ms is not None, "Latency should be reported"
        assert latency_ms < 5000, f"Health check latency {latency_ms}ms too high"

    @pytest.mark.asyncio
    async def test_multiple_concurrent_requests(self, gpt4o_service):
        """Test handling multiple concurrent classification requests."""
        import asyncio

        messages = [
            "I forgot my password",
            "The elevator is broken",
            "I need a transcript",
            "When is my financial aid coming?",
            "I want to appeal my grade",
        ]

        # Run all classifications concurrently
        tasks = [gpt4o_service.classify_intent(msg) for msg in messages]
        results = await asyncio.gather(*tasks)

        # All should complete successfully
        assert len(results) == len(messages), "All requests should complete"
        for result in results:
            assert result.intent is not None, "Each result should have an intent"
            assert result.confidence > 0, "Each result should have confidence"


# =============================================================================
# Accuracy Metrics
# =============================================================================

class TestGPT4oAccuracyMetrics:
    """Calculate and report accuracy metrics."""

    @pytest.mark.asyncio
    async def test_overall_classification_accuracy(self, gpt4o_service):
        """Calculate overall intent classification accuracy."""
        # Sample of test cases for accuracy measurement
        test_cases = [
            ("I forgot my password", "ACCOUNT_ACCESS", "IT"),
            ("Can't log into Canvas", "ACCOUNT_ACCESS", "IT"),
            ("I need a transcript", "ACADEMIC_RECORDS", "REGISTRAR"),
            ("When will my financial aid come?", "FINANCIAL", "FINANCIAL_AID"),
            ("The elevator is broken", "FACILITIES", "FACILITIES"),
            ("I lost my ID", "STUDENT_SERVICES", "STUDENT_AFFAIRS"),
            ("I want to appeal my grade", "POLICY_EXCEPTION", "ESCALATE_TO_HUMAN"),
            ("I need to talk to a person", "HUMAN_REQUEST", "ESCALATE_TO_HUMAN"),
        ]

        category_correct = 0
        department_correct = 0
        total = len(test_cases)

        for message, expected_category, expected_dept in test_cases:
            result = await gpt4o_service.classify_intent(message)

            if result.intent_category.value == expected_category:
                category_correct += 1
            if result.department_suggestion.value == expected_dept:
                department_correct += 1

        category_accuracy = category_correct / total
        department_accuracy = department_correct / total

        # Report metrics
        print(f"\n=== GPT-4o Accuracy Metrics ===")
        print(f"Category Accuracy: {category_accuracy:.1%} ({category_correct}/{total})")
        print(f"Department Accuracy: {department_accuracy:.1%} ({department_correct}/{total})")

        # Assert minimum accuracy thresholds
        assert category_accuracy >= 0.75, (
            f"Category accuracy {category_accuracy:.1%} below 75% threshold"
        )
        assert department_accuracy >= 0.75, (
            f"Department accuracy {department_accuracy:.1%} below 75% threshold"
        )
