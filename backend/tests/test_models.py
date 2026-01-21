"""
Tests for data models and schemas.
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from app.models.enums import (
    ActionStatus,
    Department,
    EscalationReason,
    IntentCategory,
    Priority,
    Sentiment,
)
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    QueryResult,
    RoutingDecision,
    ActionResult,
    KnowledgeArticle,
    Session,
    ConversationTurn,
    AuditLog,
)


class TestEnums:
    """Test enum definitions."""

    def test_department_values(self):
        """Test department enum has expected values."""
        assert Department.IT.value == "IT"
        assert Department.REGISTRAR.value == "REGISTRAR"
        assert Department.FINANCIAL_AID.value == "FINANCIAL_AID"
        assert Department.ESCALATE_TO_HUMAN.value == "ESCALATE_TO_HUMAN"

    def test_priority_ordering(self):
        """Test priority enum values."""
        priorities = [Priority.LOW, Priority.MEDIUM, Priority.HIGH, Priority.URGENT]
        assert len(priorities) == 4
        assert Priority.URGENT.value == "URGENT"

    def test_action_status_values(self):
        """Test action status enum values."""
        assert ActionStatus.CREATED.value == "created"
        assert ActionStatus.ESCALATED.value == "escalated"
        assert ActionStatus.PENDING_CLARIFICATION.value == "pending_clarification"


class TestChatRequest:
    """Test ChatRequest schema."""

    def test_valid_request(self):
        """Test creating a valid chat request."""
        request = ChatRequest(message="I forgot my password")
        assert request.message == "I forgot my password"
        assert request.session_id is None

    def test_request_with_session(self):
        """Test chat request with session ID."""
        session_id = uuid4()
        request = ChatRequest(message="Follow up", session_id=session_id)
        assert request.session_id == session_id

    def test_message_min_length(self):
        """Test message minimum length validation."""
        with pytest.raises(ValueError):
            ChatRequest(message="")

    def test_message_max_length(self):
        """Test message maximum length validation."""
        long_message = "x" * 2001
        with pytest.raises(ValueError):
            ChatRequest(message=long_message)


class TestKnowledgeArticle:
    """Test KnowledgeArticle schema."""

    def test_valid_article(self):
        """Test creating a valid knowledge article."""
        article = KnowledgeArticle(
            article_id="kb-001",
            title="How to Reset Password",
            url="https://kb.example.com/password",
            relevance_score=0.95,
        )
        assert article.article_id == "kb-001"
        assert article.relevance_score == 0.95

    def test_relevance_score_range(self):
        """Test relevance score must be between 0 and 1."""
        with pytest.raises(ValueError):
            KnowledgeArticle(
                article_id="kb-001",
                title="Test",
                url="https://example.com",
                relevance_score=1.5,
            )


class TestChatResponse:
    """Test ChatResponse schema."""

    def test_valid_response(self):
        """Test creating a valid chat response."""
        response = ChatResponse(
            session_id=uuid4(),
            ticket_id="TKT-IT-20260120-0001",
            department=Department.IT,
            status=ActionStatus.CREATED,
            message="Ticket created",
            escalated=False,
        )
        assert response.status == ActionStatus.CREATED
        assert response.escalated is False

    def test_valid_ticket_id_format(self):
        """Test valid ticket ID format is accepted."""
        response = ChatResponse(
            session_id=uuid4(),
            ticket_id="TKT-REG-20260120-0042",
            status=ActionStatus.CREATED,
            message="Created",
            escalated=False,
        )
        assert response.ticket_id == "TKT-REG-20260120-0042"

    def test_invalid_ticket_id_format(self):
        """Test invalid ticket ID format is rejected."""
        with pytest.raises(ValueError):
            ChatResponse(
                session_id=uuid4(),
                ticket_id="INVALID-ID",
                status=ActionStatus.CREATED,
                message="Created",
                escalated=False,
            )


class TestQueryResult:
    """Test QueryResult schema."""

    def test_valid_query_result(self):
        """Test creating a valid query result."""
        result = QueryResult(
            intent="password_reset",
            intent_category=IntentCategory.ACCOUNT_ACCESS,
            department_suggestion=Department.IT,
            confidence=0.92,
        )
        assert result.intent == "password_reset"
        assert result.confidence == 0.92
        assert result.pii_detected is False

    def test_confidence_range(self):
        """Test confidence must be between 0 and 1."""
        with pytest.raises(ValueError):
            QueryResult(
                intent="test",
                intent_category=IntentCategory.GENERAL_INQUIRY,
                department_suggestion=Department.IT,
                confidence=1.5,
            )


class TestRoutingDecision:
    """Test RoutingDecision schema."""

    def test_valid_routing(self):
        """Test creating a valid routing decision."""
        decision = RoutingDecision(
            department=Department.IT,
            priority=Priority.MEDIUM,
            escalate_to_human=False,
            suggested_sla_hours=4,
        )
        assert decision.department == Department.IT
        assert decision.escalation_reason is None

    def test_escalation_requires_reason(self):
        """Test escalation requires a reason."""
        with pytest.raises(ValueError):
            RoutingDecision(
                department=Department.ESCALATE_TO_HUMAN,
                priority=Priority.URGENT,
                escalate_to_human=True,
                escalation_reason=None,  # Should fail
                suggested_sla_hours=1,
            )

    def test_escalation_with_reason(self):
        """Test escalation with valid reason."""
        decision = RoutingDecision(
            department=Department.ESCALATE_TO_HUMAN,
            priority=Priority.URGENT,
            escalate_to_human=True,
            escalation_reason=EscalationReason.POLICY_KEYWORD_DETECTED,
            suggested_sla_hours=1,
        )
        assert decision.escalate_to_human is True
        assert decision.escalation_reason == EscalationReason.POLICY_KEYWORD_DETECTED


class TestSession:
    """Test Session schema."""

    def test_valid_session(self):
        """Test creating a valid session."""
        now = datetime.now(timezone.utc)
        session = Session(
            session_id=uuid4(),
            student_id_hash="a" * 64,  # SHA-256 hash is 64 chars
            created_at=now,
            last_active=now,
        )
        assert session.clarification_attempts == 0
        assert session.ttl == 7776000

    def test_student_id_hash_length(self):
        """Test student ID hash must be 64 characters."""
        now = datetime.now(timezone.utc)
        with pytest.raises(ValueError):
            Session(
                session_id=uuid4(),
                student_id_hash="tooshort",
                created_at=now,
                last_active=now,
            )

    def test_clarification_attempts_max(self):
        """Test clarification attempts maximum."""
        now = datetime.now(timezone.utc)
        with pytest.raises(ValueError):
            Session(
                session_id=uuid4(),
                student_id_hash="a" * 64,
                created_at=now,
                last_active=now,
                clarification_attempts=5,  # Max is 3
            )


class TestAuditLog:
    """Test AuditLog schema."""

    def test_valid_audit_log(self):
        """Test creating a valid audit log."""
        now = datetime.now(timezone.utc)
        log = AuditLog(
            log_id=uuid4(),
            timestamp=now,
            student_id_hash="b" * 64,
            session_id=uuid4(),
            detected_intent="password_reset",
            confidence_score=0.92,
            routed_department=Department.IT,
            escalated=False,
            pii_detected=False,
            sentiment=Sentiment.NEUTRAL,
            response_time_ms=150,
        )
        assert log.escalated is False
        assert log.response_time_ms == 150

    def test_escalation_requires_reason_in_audit(self):
        """Test escalated audit log requires reason."""
        now = datetime.now(timezone.utc)
        with pytest.raises(ValueError):
            AuditLog(
                log_id=uuid4(),
                timestamp=now,
                student_id_hash="b" * 64,
                session_id=uuid4(),
                detected_intent="test",
                confidence_score=0.5,
                routed_department=Department.ESCALATE_TO_HUMAN,
                escalated=True,
                escalation_reason=None,  # Should fail
                pii_detected=False,
                sentiment=Sentiment.FRUSTRATED,
                response_time_ms=200,
            )
