"""
API routes for the Front Door Support Agent.
Implements the OpenAPI contract.
"""

import hashlib
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status

from app.agents import ActionAgent, QueryAgent, RouterAgent
from app.core.config import Settings, get_settings
from app.core.dependencies import (
    get_audit_log,
    get_knowledge_service,
    get_llm_service,
    get_session_store,
    get_ticket_service,
)
from app.services.interfaces import (
    AuditLogInterface,
    KnowledgeServiceInterface,
    LLMServiceInterface,
    SessionStoreInterface,
    TicketServiceInterface,
)
from app.models.enums import ActionStatus, Department, Priority, TicketStatus
from app.models.schemas import (
    AuditLog,
    ChatRequest,
    ChatResponse,
    ConversationTurn,
    ErrorResponse,
    HealthStatus,
    KnowledgeArticle,
    KnowledgeSearchResponse,
    ServiceHealth,
    Session,
    TicketListResponse,
    TicketStatusResponse,
    TicketSummary,
)

router = APIRouter()


# =============================================================================
# Chat Endpoint
# =============================================================================


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        503: {"model": ChatResponse, "description": "Service degraded"},
    },
    tags=["Chat"],
    summary="Submit a support query",
    description="""
    Process a student's support query through the three-agent pipeline:
    1. QueryAgent: Detect intent and extract entities
    2. RouterAgent: Determine routing and escalation
    3. ActionAgent: Create ticket and retrieve KB articles
    """,
)
async def submit_query(
    *,
    message: str = Body(..., min_length=1, max_length=2000),
    session_id: str | None = Body(None),
    settings: Settings = Depends(get_settings),
    llm_service: LLMServiceInterface = Depends(get_llm_service),
    ticket_service: TicketServiceInterface = Depends(get_ticket_service),
    knowledge_service: KnowledgeServiceInterface = Depends(get_knowledge_service),
    session_store: SessionStoreInterface = Depends(get_session_store),
    audit_log: AuditLogInterface = Depends(get_audit_log),
) -> ChatResponse:
    """Submit a support query and receive routing, ticket, and KB articles."""
    start_time = datetime.now(timezone.utc)

    # For demo/testing, use a mock student ID hash
    # In production, this would come from authenticated session
    student_id_hash = hashlib.sha256(b"demo_student").hexdigest()

    # Get or create session
    session: Optional[Session] = None
    if session_id:
        from uuid import UUID as UUIDType
        session = await session_store.get_session(UUIDType(session_id))

    if session is None:
        session = Session(
            session_id=uuid4(),
            student_id_hash=student_id_hash,
            created_at=start_time,
            last_active=start_time,
            conversation_history=[],
            clarification_attempts=0,
            ttl=settings.session_ttl_seconds,
        )
        await session_store.create_session(session)

    # Initialize agents
    query_agent = QueryAgent(llm_service)
    router_agent = RouterAgent(settings)
    action_agent = ActionAgent(ticket_service, knowledge_service, llm_service)

    # Step 1: QueryAgent - Analyze the message
    query_result = await query_agent.analyze(
        message=message,
        conversation_history=session.conversation_history,
    )

    # Step 2: RouterAgent - Check if clarification needed
    if router_agent.needs_clarification(query_result, session.clarification_attempts):
        # Generate clarification question
        possible_intents = [query_result.intent, "general_question"]
        clarification = await query_agent.generate_clarification(
            message=message,
            possible_intents=possible_intents,
        )

        # Update session
        session.clarification_attempts += 1
        session.last_active = datetime.now(timezone.utc)
        await session_store.update_session(session)

        # Return clarification response
        return ChatResponse(
            session_id=session.session_id,
            ticket_id=None,
            department=None,
            status=ActionStatus.PENDING_CLARIFICATION,
            message=clarification,
            knowledge_articles=[],
            escalated=False,
            escalation_reason=None,
            estimated_response_time=None,
        )

    # Step 2: RouterAgent - Make routing decision
    routing_decision = router_agent.route(
        query_result=query_result,
        clarification_attempts=session.clarification_attempts,
    )

    # Step 3: ActionAgent - Execute actions
    action_result = await action_agent.execute(
        query_result=query_result,
        routing_decision=routing_decision,
        student_id_hash=student_id_hash,
        original_message=message,
    )

    # Update session with this turn
    turn = ConversationTurn(
        turn_number=len(session.conversation_history) + 1,
        timestamp=datetime.now(timezone.utc),
        intent=query_result.intent,
        ticket_id=action_result.ticket_id,
        escalated=action_result.escalated,
    )
    session.conversation_history.append(turn)
    session.last_active = datetime.now(timezone.utc)
    session.clarification_attempts = 0  # Reset on successful routing
    await session_store.update_session(session)

    # Calculate response time
    end_time = datetime.now(timezone.utc)
    response_time_ms = int((end_time - start_time).total_seconds() * 1000)

    # Log to audit
    audit_entry = AuditLog(
        log_id=uuid4(),
        timestamp=end_time,
        student_id_hash=student_id_hash,
        session_id=session.session_id,
        detected_intent=query_result.intent,
        confidence_score=query_result.confidence,
        routed_department=routing_decision.department,
        ticket_id=action_result.ticket_id,
        escalated=action_result.escalated,
        escalation_reason=routing_decision.escalation_reason.value if routing_decision.escalation_reason else None,
        pii_detected=query_result.pii_detected,
        sentiment=query_result.sentiment,
        response_time_ms=response_time_ms,
    )
    await audit_log.log_interaction(audit_entry)

    return ChatResponse(
        session_id=session.session_id,
        ticket_id=action_result.ticket_id,
        department=action_result.department if action_result.department != Department.ESCALATE_TO_HUMAN else None,
        status=action_result.status,
        message=action_result.user_message,
        knowledge_articles=action_result.knowledge_articles,
        escalated=action_result.escalated,
        escalation_reason=routing_decision.escalation_reason,
        estimated_response_time=action_result.estimated_response_time,
    )


# =============================================================================
# Ticket Endpoints
# =============================================================================


@router.get(
    "/tickets/{ticket_id}",
    response_model=TicketStatusResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Ticket not found"},
    },
    tags=["Tickets"],
    summary="Get ticket status",
)
async def get_ticket_status(
    ticket_id: str,
    ticket_service: TicketServiceInterface = Depends(get_ticket_service),
) -> TicketStatusResponse:
    """Retrieve the current status of a support ticket."""
    result = await ticket_service.get_ticket_status(ticket_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": f"Ticket {ticket_id} not found"},
        )
    return result


@router.get(
    "/tickets",
    response_model=TicketListResponse,
    tags=["Tickets"],
    summary="List user's tickets",
)
async def list_user_tickets(
    ticket_service: TicketServiceInterface = Depends(get_ticket_service),
    status_filter: Optional[str] = Query(
        None,
        alias="status",
        description="Filter by ticket status",
    ),
    limit: int = Query(10, ge=1, le=50, description="Maximum tickets to return"),
) -> TicketListResponse:
    """Retrieve all tickets for the authenticated student."""
    # In production, get student_id_hash from auth context
    student_id_hash = hashlib.sha256(b"demo_student").hexdigest()

    tickets = await ticket_service.list_user_tickets(
        student_id_hash=student_id_hash,
        status_filter=status_filter,
        limit=limit,
    )

    return TicketListResponse(
        tickets=tickets,
        total=len(tickets),
    )


# =============================================================================
# Knowledge Base Endpoint
# =============================================================================


@router.get(
    "/knowledge/search",
    response_model=KnowledgeSearchResponse,
    tags=["Knowledge"],
    summary="Search knowledge base",
    description="Search the knowledge base for relevant articles. Available without authentication.",
)
async def search_knowledge(
    knowledge_service: KnowledgeServiceInterface = Depends(get_knowledge_service),
    q: str = Query(..., min_length=2, max_length=500, description="Search query"),
    department: Optional[Department] = Query(None, description="Filter by department"),
    limit: int = Query(3, ge=1, le=10, description="Maximum articles to return"),
) -> KnowledgeSearchResponse:
    """Search the knowledge base for relevant articles."""
    articles = await knowledge_service.search(
        query=q,
        department=department,
        limit=limit,
    )

    return KnowledgeSearchResponse(
        articles=articles,
        total_results=len(articles),
    )


# =============================================================================
# Health Check Endpoint
# =============================================================================


@router.get(
    "/health",
    response_model=HealthStatus,
    responses={
        503: {"model": HealthStatus, "description": "System degraded"},
    },
    tags=["Health"],
    summary="Health check",
)
async def health_check(
    llm_service: LLMServiceInterface = Depends(get_llm_service),
    ticket_service: TicketServiceInterface = Depends(get_ticket_service),
    knowledge_service: KnowledgeServiceInterface = Depends(get_knowledge_service),
    session_store: SessionStoreInterface = Depends(get_session_store),
) -> HealthStatus:
    """Check system health and dependency status."""
    services: dict[str, ServiceHealth] = {}

    # Check each service
    llm_healthy, llm_latency, llm_error = await llm_service.health_check()
    services["llm"] = ServiceHealth(
        status="up" if llm_healthy else "down",
        latency_ms=llm_latency,
        error=llm_error,
    )

    ticket_healthy, ticket_latency, ticket_error = await ticket_service.health_check()
    services["ticketing"] = ServiceHealth(
        status="up" if ticket_healthy else "down",
        latency_ms=ticket_latency,
        error=ticket_error,
    )

    kb_healthy, kb_latency, kb_error = await knowledge_service.health_check()
    services["knowledge_base"] = ServiceHealth(
        status="up" if kb_healthy else "down",
        latency_ms=kb_latency,
        error=kb_error,
    )

    session_healthy, session_latency, session_error = await session_store.health_check()
    services["session_store"] = ServiceHealth(
        status="up" if session_healthy else "down",
        latency_ms=session_latency,
        error=session_error,
    )

    # Determine overall status
    all_healthy = all(s.status == "up" for s in services.values())
    any_down = any(s.status == "down" for s in services.values())

    if all_healthy:
        overall_status = "healthy"
    elif any_down:
        overall_status = "unhealthy"
    else:
        overall_status = "degraded"

    return HealthStatus(
        status=overall_status,
        timestamp=datetime.now(timezone.utc),
        services=services,
    )


# =============================================================================
# Admin Endpoints (Ticket Triage & Management)
# =============================================================================


@router.get(
    "/admin/tickets",
    response_model=TicketListResponse,
    tags=["Admin"],
    summary="List all tickets (admin)",
    description="List all tickets across all users for admin triage and management.",
)
async def admin_list_all_tickets(
    ticket_service: TicketServiceInterface = Depends(get_ticket_service),
    status_filter: Optional[str] = Query(
        None,
        alias="status",
        description="Filter by ticket status (open, in_progress, pending_info, resolved, closed)",
    ),
    department: Optional[Department] = Query(
        None,
        description="Filter by department",
    ),
    limit: int = Query(50, ge=1, le=100, description="Maximum tickets to return"),
) -> TicketListResponse:
    """Retrieve all tickets for admin triage."""
    tickets = await ticket_service.list_all_tickets(
        status_filter=status_filter,
        department_filter=department,
        limit=limit,
    )

    return TicketListResponse(
        tickets=tickets,
        total=len(tickets),
    )


from pydantic import BaseModel, Field


class TicketUpdateRequest(BaseModel):
    """Request body for updating a ticket."""
    status: TicketStatus = Field(..., description="New ticket status")
    assigned_to: Optional[str] = Field(None, description="Assignee name")
    resolution_summary: Optional[str] = Field(None, description="Resolution notes (for closed tickets)")


@router.patch(
    "/admin/tickets/{ticket_id}",
    response_model=TicketStatusResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Ticket not found"},
    },
    tags=["Admin"],
    summary="Update ticket status (admin)",
    description="Update a ticket's status, assignee, or resolution for triage purposes.",
)
async def admin_update_ticket(
    ticket_id: str,
    *,
    new_status: TicketStatus = Body(..., alias="status", description="New ticket status"),
    assigned_to: Optional[str] = Body(None, description="Assignee name"),
    resolution_summary: Optional[str] = Body(None, description="Resolution notes"),
    ticket_service: TicketServiceInterface = Depends(get_ticket_service),
) -> TicketStatusResponse:
    """Update a ticket for triage/management."""
    result = await ticket_service.update_ticket_status(
        ticket_id=ticket_id,
        new_status=new_status,
        assigned_to=assigned_to,
        resolution_summary=resolution_summary,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": f"Ticket {ticket_id} not found"},
        )

    return result


@router.delete(
    "/admin/tickets/{ticket_id}",
    responses={
        404: {"model": ErrorResponse, "description": "Ticket not found"},
    },
    tags=["Admin"],
    summary="Delete a ticket (admin)",
    description="Permanently delete a ticket from the system.",
)
async def admin_delete_ticket(
    ticket_id: str,
    ticket_service: TicketServiceInterface = Depends(get_ticket_service),
) -> dict:
    """Delete a ticket (admin action)."""
    deleted = await ticket_service.delete_ticket(ticket_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": f"Ticket {ticket_id} not found"},
        )

    return {"message": f"Ticket {ticket_id} deleted successfully"}
