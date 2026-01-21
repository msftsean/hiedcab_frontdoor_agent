"""
Pydantic schemas for the Front Door Support Agent API.
Matches the data model specification and OpenAPI contract.
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.enums import (
    ActionStatus,
    Department,
    EscalationReason,
    IntentCategory,
    Priority,
    Sentiment,
    TicketStatus,
)


# =============================================================================
# API Request/Response Models
# =============================================================================


class ChatRequest(BaseModel):
    """Request body for the /api/chat endpoint."""
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Student's support query"
    )
    session_id: Optional[UUID] = Field(
        default=None,
        description="Existing session ID for multi-turn conversations"
    )


class KnowledgeArticle(BaseModel):
    """A relevant help article from the knowledge base."""
    article_id: str = Field(..., description="Unique article identifier")
    title: str = Field(..., description="Article title")
    url: str = Field(..., description="Link to full article")
    snippet: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Brief preview"
    )
    relevance_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Search relevance score"
    )
    department: Optional[Department] = Field(
        default=None,
        description="Owning department"
    )


class ChatResponse(BaseModel):
    """Response body for the /api/chat endpoint."""
    session_id: UUID = Field(..., description="Session ID for follow-up queries")
    ticket_id: Optional[str] = Field(
        default=None,
        description="Created ticket ID (if any)"
    )
    department: Optional[Department] = Field(
        default=None,
        description="Routed department"
    )
    status: ActionStatus = Field(..., description="Outcome status")
    message: str = Field(..., description="User-friendly response message")
    knowledge_articles: list[KnowledgeArticle] = Field(
        default_factory=list,
        max_length=3,
        description="Retrieved KB articles"
    )
    escalated: bool = Field(..., description="Whether request was escalated to human")
    escalation_reason: Optional[EscalationReason] = Field(
        default=None,
        description="Reason for escalation"
    )
    estimated_response_time: Optional[str] = Field(
        default=None,
        description="Human-readable SLA estimate"
    )

    @field_validator("ticket_id")
    @classmethod
    def validate_ticket_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate ticket ID format: TKT-{DEPT}-{YYYYMMDD}-{SEQ}"""
        if v is not None:
            import re
            pattern = r"^TKT-[A-Z]{2,3}-\d{8}-\d{4}$"
            if not re.match(pattern, v):
                raise ValueError(
                    f"Invalid ticket ID format. Expected TKT-XX-YYYYMMDD-NNNN, got {v}"
                )
        return v


class TicketStatusResponse(BaseModel):
    """Response for GET /api/tickets/{ticket_id}."""
    ticket_id: str = Field(..., description="Ticket identifier")
    department: Department = Field(..., description="Assigned department")
    status: TicketStatus = Field(..., description="Current ticket status")
    priority: Optional[Priority] = Field(default=None, description="Priority level")
    summary: Optional[str] = Field(default=None, description="Brief description")
    description: Optional[str] = Field(default=None, description="Full request content")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    assigned_to: Optional[str] = Field(default=None, description="Assigned agent name")
    resolution_summary: Optional[str] = Field(
        default=None,
        description="Resolution details if resolved"
    )


class TicketSummary(BaseModel):
    """Summary of a ticket for list views."""
    ticket_id: str = Field(..., description="Ticket identifier")
    department: Department = Field(..., description="Assigned department")
    status: str = Field(..., description="Current status")
    created_at: datetime = Field(..., description="Creation timestamp")
    summary: str = Field(..., max_length=200, description="Brief description")
    description: Optional[str] = Field(default=None, description="Full request content")


class TicketListResponse(BaseModel):
    """Response for GET /api/tickets."""
    tickets: list[TicketSummary] = Field(default_factory=list)
    total: int = Field(..., description="Total number of tickets")


class KnowledgeSearchResponse(BaseModel):
    """Response for GET /api/knowledge/search."""
    articles: list[KnowledgeArticle] = Field(default_factory=list)
    total_results: int = Field(..., description="Total matching articles")


class ServiceHealth(BaseModel):
    """Health status of a single service."""
    status: str = Field(..., description="Service status: up, down, degraded")
    latency_ms: Optional[int] = Field(default=None, description="Response latency")
    error: Optional[str] = Field(default=None, description="Error message if any")


class HealthStatus(BaseModel):
    """Response for GET /api/health."""
    status: str = Field(..., description="Overall status: healthy, degraded, unhealthy")
    timestamp: datetime = Field(..., description="Health check timestamp")
    services: dict[str, ServiceHealth] = Field(
        default_factory=dict,
        description="Status of individual services"
    )


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict[str, Any]] = Field(default=None, description="Additional details")


# =============================================================================
# Internal Agent Models
# =============================================================================


class QueryResult(BaseModel):
    """Output of the QueryAgent's intent detection and entity extraction."""
    intent: str = Field(..., description="Primary detected intent")
    intent_category: IntentCategory = Field(..., description="Category grouping")
    department_suggestion: Department = Field(..., description="Suggested target department")
    entities: dict[str, Any] = Field(
        default_factory=dict,
        description="Extracted entities"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Classification confidence"
    )
    requires_escalation: bool = Field(
        default=False,
        description="Pre-routing escalation flag"
    )
    pii_detected: bool = Field(default=False, description="Whether PII was found")
    pii_types: list[str] = Field(
        default_factory=list,
        description="Types of PII detected"
    )
    sentiment: Sentiment = Field(default=Sentiment.NEUTRAL, description="Detected sentiment")
    urgency_indicators: list[str] = Field(
        default_factory=list,
        description="Urgency signals found"
    )


class RoutingDecision(BaseModel):
    """Output of the RouterAgent's routing logic."""
    department: Department = Field(..., description="Target department for routing")
    priority: Priority = Field(..., description="Request priority level")
    escalate_to_human: bool = Field(
        default=False,
        description="Whether human review required"
    )
    escalation_reason: Optional[EscalationReason] = Field(
        default=None,
        description="Reason for escalation"
    )
    suggested_sla_hours: int = Field(
        ...,
        gt=0,
        description="Expected response time in hours"
    )
    routing_rules_applied: list[str] = Field(
        default_factory=list,
        description="Which rules determined this decision"
    )

    @field_validator("escalation_reason")
    @classmethod
    def require_reason_if_escalated(
        cls, v: Optional[EscalationReason], info
    ) -> Optional[EscalationReason]:
        """Ensure escalation_reason is provided if escalate_to_human is True."""
        escalate = info.data.get("escalate_to_human", False)
        if escalate and v is None:
            raise ValueError("escalation_reason is required when escalate_to_human is True")
        return v


class ActionResult(BaseModel):
    """Output of the ActionAgent's execution."""
    ticket_id: Optional[str] = Field(
        default=None,
        description="Created ticket ID"
    )
    ticket_url: Optional[str] = Field(
        default=None,
        description="Link to ticket in ticketing system"
    )
    department: Department = Field(..., description="Department that received the request")
    status: ActionStatus = Field(..., description="Outcome status")
    knowledge_articles: list[KnowledgeArticle] = Field(
        default_factory=list,
        max_length=3,
        description="Retrieved KB articles"
    )
    estimated_response_time: str = Field(
        ...,
        description="Human-readable SLA"
    )
    escalated: bool = Field(default=False, description="Whether escalation occurred")
    user_message: str = Field(
        ...,
        description="Friendly response to display to student"
    )

    @field_validator("ticket_id")
    @classmethod
    def validate_ticket_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate ticket ID format."""
        if v is not None:
            import re
            pattern = r"^TKT-[A-Z]{2,3}-\d{8}-\d{4}$"
            if not re.match(pattern, v):
                raise ValueError(
                    f"Invalid ticket ID format. Expected TKT-XX-YYYYMMDD-NNNN, got {v}"
                )
        return v


# =============================================================================
# Session & Audit Models
# =============================================================================


class ConversationTurn(BaseModel):
    """A single turn in a conversation."""
    turn_number: int = Field(..., ge=1, description="Sequential turn number")
    timestamp: datetime = Field(..., description="When this turn occurred")
    intent: str = Field(..., description="Detected intent for this turn")
    ticket_id: Optional[str] = Field(
        default=None,
        description="Ticket created in this turn"
    )
    escalated: bool = Field(default=False, description="Whether this turn resulted in escalation")


class Session(BaseModel):
    """Student's conversation context for multi-turn interactions."""
    session_id: UUID = Field(..., description="Unique identifier for the session")
    student_id_hash: str = Field(
        ...,
        min_length=64,
        max_length=64,
        description="Hashed student ID (SHA-256)"
    )
    created_at: datetime = Field(..., description="Session creation timestamp")
    last_active: datetime = Field(..., description="Last interaction timestamp")
    conversation_history: list[ConversationTurn] = Field(
        default_factory=list,
        max_length=50,
        description="List of conversation turns"
    )
    clarification_attempts: int = Field(
        default=0,
        ge=0,
        le=3,
        description="Count of disambiguation attempts"
    )
    ttl: int = Field(
        default=7776000,
        description="Time-to-live in seconds (90 days)"
    )


class AuditLog(BaseModel):
    """Immutable record of each interaction for compliance and analytics."""
    log_id: UUID = Field(..., description="Unique identifier for this log entry")
    timestamp: datetime = Field(..., description="When the interaction occurred")
    student_id_hash: str = Field(
        ...,
        min_length=64,
        max_length=64,
        description="Hashed student ID"
    )
    session_id: UUID = Field(..., description="Reference to parent session")
    detected_intent: str = Field(..., description="Intent classification result")
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Classification confidence"
    )
    routed_department: Department = Field(..., description="Where request was routed")
    ticket_id: Optional[str] = Field(
        default=None,
        description="Created ticket ID"
    )
    escalated: bool = Field(default=False, description="Whether escalation occurred")
    escalation_reason: Optional[str] = Field(
        default=None,
        description="Reason for escalation"
    )
    pii_detected: bool = Field(default=False, description="Whether PII was detected")
    sentiment: Sentiment = Field(..., description="Detected sentiment")
    response_time_ms: int = Field(
        ...,
        ge=0,
        description="End-to-end response time"
    )

    @field_validator("escalation_reason")
    @classmethod
    def require_reason_if_escalated(
        cls, v: Optional[str], info
    ) -> Optional[str]:
        """Ensure escalation_reason is provided if escalated is True."""
        escalated = info.data.get("escalated", False)
        if escalated and v is None:
            raise ValueError("escalation_reason is required when escalated is True")
        return v
