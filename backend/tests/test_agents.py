"""
Tests for agent implementations.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.agents import QueryAgent, RouterAgent, ActionAgent
from app.core.config import Settings
from app.models.enums import (
    ActionStatus,
    Department,
    EscalationReason,
    IntentCategory,
    Priority,
    Sentiment,
)
from app.models.schemas import QueryResult, RoutingDecision


class TestQueryAgent:
    """Tests for QueryAgent."""

    @pytest.fixture
    def mock_llm(self):
        """Create mock LLM service."""
        mock = MagicMock()
        mock.classify_intent = AsyncMock(
            return_value=QueryResult(
                intent="password_reset",
                intent_category=IntentCategory.ACCOUNT_ACCESS,
                department_suggestion=Department.IT,
                confidence=0.92,
                pii_detected=False,
                sentiment=Sentiment.NEUTRAL,
            )
        )
        mock.generate_clarification_question = AsyncMock(
            return_value="Are you asking about password reset or account access?"
        )
        return mock

    @pytest.fixture
    def agent(self, mock_llm):
        """Create QueryAgent with mock LLM."""
        return QueryAgent(mock_llm)

    @pytest.mark.asyncio
    async def test_analyze_returns_query_result(self, agent, mock_llm):
        """Test analyze method returns QueryResult."""
        result = await agent.analyze("I forgot my password")

        assert isinstance(result, QueryResult)
        assert result.intent == "password_reset"
        assert result.confidence == 0.92
        mock_llm.classify_intent.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_clarification(self, agent, mock_llm):
        """Test clarification question generation."""
        question = await agent.generate_clarification(
            "I need help",
            ["password_reset", "general_question"],
        )

        assert "?" in question or "asking" in question
        mock_llm.generate_clarification_question.assert_called_once()


class TestRouterAgent:
    """Tests for RouterAgent."""

    @pytest.fixture
    def settings(self):
        """Create test settings."""
        return Settings(
            confidence_threshold=0.70,
            max_clarification_attempts=3,
            sla_urgent_hours=1,
            sla_high_hours=4,
            sla_medium_hours=24,
            sla_low_hours=72,
        )

    @pytest.fixture
    def agent(self, settings):
        """Create RouterAgent with settings."""
        return RouterAgent(settings)

    def test_route_standard_request(self, agent):
        """Test routing a standard request."""
        query_result = QueryResult(
            intent="password_reset",
            intent_category=IntentCategory.ACCOUNT_ACCESS,
            department_suggestion=Department.IT,
            confidence=0.92,
            sentiment=Sentiment.NEUTRAL,
        )

        decision = agent.route(query_result)

        assert isinstance(decision, RoutingDecision)
        assert decision.department == Department.IT
        assert decision.priority == Priority.MEDIUM
        assert decision.escalate_to_human is False

    def test_route_escalates_low_confidence(self, agent):
        """Test routing escalates when confidence is too low after max attempts."""
        query_result = QueryResult(
            intent="general_question",
            intent_category=IntentCategory.GENERAL_INQUIRY,
            department_suggestion=Department.IT,
            confidence=0.45,
            sentiment=Sentiment.NEUTRAL,
        )

        decision = agent.route(query_result, clarification_attempts=3)

        assert decision.escalate_to_human is True
        assert decision.escalation_reason == EscalationReason.MAX_CLARIFICATIONS_EXCEEDED

    def test_route_escalates_policy_intent(self, agent):
        """Test routing escalates for policy-related intents."""
        query_result = QueryResult(
            intent="grade_appeal",
            intent_category=IntentCategory.POLICY_EXCEPTION,
            department_suggestion=Department.STUDENT_AFFAIRS,
            confidence=0.88,
            requires_escalation=True,
            sentiment=Sentiment.NEUTRAL,
        )

        decision = agent.route(query_result)

        assert decision.escalate_to_human is True
        assert decision.department == Department.ESCALATE_TO_HUMAN

    def test_route_high_priority_frustrated(self, agent):
        """Test frustrated sentiment increases priority."""
        query_result = QueryResult(
            intent="login_issues",
            intent_category=IntentCategory.ACCOUNT_ACCESS,
            department_suggestion=Department.IT,
            confidence=0.85,
            sentiment=Sentiment.FRUSTRATED,
        )

        decision = agent.route(query_result)

        assert decision.priority == Priority.HIGH

    def test_route_urgent_priority_escalation_flag(self, agent):
        """Test requires_escalation flag sets urgent priority."""
        query_result = QueryResult(
            intent="sensitive_topic",
            intent_category=IntentCategory.HUMAN_REQUEST,
            department_suggestion=Department.ESCALATE_TO_HUMAN,
            confidence=0.90,
            requires_escalation=True,
            sentiment=Sentiment.URGENT,
        )

        decision = agent.route(query_result)

        assert decision.priority == Priority.URGENT

    def test_needs_clarification_low_confidence(self, agent):
        """Test needs_clarification returns True for low confidence."""
        query_result = QueryResult(
            intent="general_question",
            intent_category=IntentCategory.GENERAL_INQUIRY,
            department_suggestion=Department.IT,
            confidence=0.55,
            sentiment=Sentiment.NEUTRAL,
        )

        assert agent.needs_clarification(query_result, clarification_attempts=0) is True
        assert agent.needs_clarification(query_result, clarification_attempts=3) is False

    def test_no_clarification_for_escalation(self, agent):
        """Test no clarification needed when escalation is required."""
        query_result = QueryResult(
            intent="request_human",
            intent_category=IntentCategory.HUMAN_REQUEST,
            department_suggestion=Department.ESCALATE_TO_HUMAN,
            confidence=0.55,
            requires_escalation=True,
            sentiment=Sentiment.NEUTRAL,
        )

        assert agent.needs_clarification(query_result, clarification_attempts=0) is False


class TestActionAgent:
    """Tests for ActionAgent."""

    @pytest.fixture
    def mock_ticket_service(self):
        """Create mock ticket service."""
        mock = MagicMock()
        mock.create_ticket = AsyncMock(
            return_value=("TKT-IT-20260120-0001", "https://tickets.example.com/TKT-IT-20260120-0001")
        )
        return mock

    @pytest.fixture
    def mock_knowledge_service(self):
        """Create mock knowledge service."""
        mock = MagicMock()
        mock.search = AsyncMock(return_value=[])
        return mock

    @pytest.fixture
    def mock_llm_service(self):
        """Create mock LLM service."""
        mock = MagicMock()
        mock.generate_response_message = AsyncMock(
            return_value="I've created a ticket for IT Support."
        )
        return mock

    @pytest.fixture
    def agent(self, mock_ticket_service, mock_knowledge_service, mock_llm_service):
        """Create ActionAgent with mocks."""
        return ActionAgent(mock_ticket_service, mock_knowledge_service, mock_llm_service)

    @pytest.mark.asyncio
    async def test_execute_creates_ticket(
        self, agent, mock_ticket_service, mock_knowledge_service
    ):
        """Test execute creates a ticket."""
        query_result = QueryResult(
            intent="password_reset",
            intent_category=IntentCategory.ACCOUNT_ACCESS,
            department_suggestion=Department.IT,
            confidence=0.92,
            sentiment=Sentiment.NEUTRAL,
        )
        routing_decision = RoutingDecision(
            department=Department.IT,
            priority=Priority.MEDIUM,
            escalate_to_human=False,
            suggested_sla_hours=24,
        )

        result = await agent.execute(
            query_result=query_result,
            routing_decision=routing_decision,
            student_id_hash="a" * 64,
            original_message="I forgot my password",
        )

        assert result.ticket_id == "TKT-IT-20260120-0001"
        assert result.status == ActionStatus.CREATED
        mock_ticket_service.create_ticket.assert_called_once()
        mock_knowledge_service.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_escalation_status(
        self, agent, mock_ticket_service
    ):
        """Test execute sets escalated status correctly."""
        query_result = QueryResult(
            intent="grade_appeal",
            intent_category=IntentCategory.POLICY_EXCEPTION,
            department_suggestion=Department.STUDENT_AFFAIRS,
            confidence=0.88,
            requires_escalation=True,
            sentiment=Sentiment.NEUTRAL,
        )
        routing_decision = RoutingDecision(
            department=Department.ESCALATE_TO_HUMAN,
            priority=Priority.URGENT,
            escalate_to_human=True,
            escalation_reason=EscalationReason.POLICY_KEYWORD_DETECTED,
            suggested_sla_hours=1,
        )

        result = await agent.execute(
            query_result=query_result,
            routing_decision=routing_decision,
            student_id_hash="a" * 64,
            original_message="I want to appeal my grade",
        )

        assert result.status == ActionStatus.ESCALATED
        assert result.escalated is True

    @pytest.mark.asyncio
    async def test_create_clarification_response(self, agent):
        """Test creating clarification response."""
        result = await agent.create_clarification_response(
            "Are you asking about your login or financial account?"
        )

        assert result.status == ActionStatus.PENDING_CLARIFICATION
        assert result.ticket_id is None
        assert "account" in result.user_message
