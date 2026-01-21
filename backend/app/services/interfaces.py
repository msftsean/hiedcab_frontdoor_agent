"""
Service interfaces (abstract base classes) for the Front Door Support Agent.
All external service integrations implement these interfaces to support
both production and mock implementations.
"""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.models.schemas import (
    AuditLog,
    KnowledgeArticle,
    QueryResult,
    Session,
    TicketStatusResponse,
    TicketSummary,
)
from app.models.enums import Department, Priority, TicketStatus


class LLMServiceInterface(ABC):
    """Interface for LLM-based intent classification and entity extraction."""

    @abstractmethod
    async def classify_intent(
        self,
        message: str,
        conversation_history: Optional[list[dict]] = None,
    ) -> QueryResult:
        """
        Analyze a user message to detect intent and extract entities.

        Args:
            message: The user's support query.
            conversation_history: Previous turns for context (if multi-turn).

        Returns:
            QueryResult with intent, entities, confidence, and metadata.
        """
        pass

    @abstractmethod
    async def generate_clarification_question(
        self,
        message: str,
        possible_intents: list[str],
    ) -> str:
        """
        Generate a clarification question when intent is ambiguous.

        Args:
            message: The ambiguous user message.
            possible_intents: List of possible intent classifications.

        Returns:
            A user-friendly clarification question.
        """
        pass

    @abstractmethod
    async def generate_response_message(
        self,
        intent: str,
        department: Department,
        ticket_id: Optional[str],
        escalated: bool,
        estimated_response_time: str,
        original_message: Optional[str] = None,
        knowledge_articles: Optional[list[KnowledgeArticle]] = None,
        kb_article_contents: Optional[list[dict]] = None,
    ) -> str:
        """
        Generate a user-friendly response message with self-service info.

        Args:
            intent: The detected intent.
            department: The routed department.
            ticket_id: Created ticket ID (if any).
            escalated: Whether the request was escalated.
            estimated_response_time: Expected response time.
            original_message: The user's original query (for context).
            knowledge_articles: List of matched KB articles (metadata).
            kb_article_contents: Full content of matched KB articles for self-service responses.

        Returns:
            A friendly message to display to the user, including self-service
            instructions from KB articles when available.
        """
        pass

    @abstractmethod
    async def health_check(self) -> tuple[bool, Optional[int], Optional[str]]:
        """
        Check LLM service health.

        Returns:
            Tuple of (is_healthy, latency_ms, error_message).
        """
        pass


class TicketServiceInterface(ABC):
    """Interface for ticketing system integration (e.g., ServiceNow)."""

    @abstractmethod
    async def create_ticket(
        self,
        department: Department,
        priority: Priority,
        summary: str,
        description: str,
        student_id_hash: str,
        entities: Optional[dict] = None,
    ) -> tuple[str, str]:
        """
        Create a support ticket in the ticketing system.

        Args:
            department: Target department.
            priority: Ticket priority.
            summary: Brief summary of the issue.
            description: Detailed description.
            student_id_hash: Hashed student identifier.
            entities: Extracted entities (building, course, etc.).

        Returns:
            Tuple of (ticket_id, ticket_url).
        """
        pass

    @abstractmethod
    async def get_ticket_status(
        self,
        ticket_id: str,
    ) -> Optional[TicketStatusResponse]:
        """
        Get the current status of a ticket.

        Args:
            ticket_id: The ticket identifier.

        Returns:
            TicketStatusResponse if found, None otherwise.
        """
        pass

    @abstractmethod
    async def list_user_tickets(
        self,
        student_id_hash: str,
        status_filter: Optional[str] = None,
        limit: int = 10,
    ) -> list[TicketSummary]:
        """
        List tickets for a specific user.

        Args:
            student_id_hash: Hashed student identifier.
            status_filter: Optional status filter.
            limit: Maximum number of tickets to return.

        Returns:
            List of ticket summaries.
        """
        pass

    # =========================================================================
    # Admin Methods
    # =========================================================================

    @abstractmethod
    async def list_all_tickets(
        self,
        status_filter: Optional[str] = None,
        department_filter: Optional[Department] = None,
        limit: int = 50,
    ) -> list[TicketSummary]:
        """
        List all tickets (admin view).

        Args:
            status_filter: Optional status filter.
            department_filter: Optional department filter.
            limit: Maximum number of tickets to return.

        Returns:
            List of ticket summaries.
        """
        pass

    @abstractmethod
    async def update_ticket_status(
        self,
        ticket_id: str,
        new_status: "TicketStatus",
        assigned_to: Optional[str] = None,
        resolution_summary: Optional[str] = None,
    ) -> Optional[TicketStatusResponse]:
        """
        Update ticket status (admin/triage action).

        Args:
            ticket_id: The ticket identifier.
            new_status: New status to set.
            assigned_to: Optional assignee name.
            resolution_summary: Optional resolution notes (for closed tickets).

        Returns:
            Updated TicketStatusResponse if found, None otherwise.
        """
        pass

    @abstractmethod
    async def delete_ticket(
        self,
        ticket_id: str,
    ) -> bool:
        """
        Delete a ticket (admin action).

        Args:
            ticket_id: The ticket identifier.

        Returns:
            True if deleted, False if not found.
        """
        pass

    @abstractmethod
    async def health_check(self) -> tuple[bool, Optional[int], Optional[str]]:
        """
        Check ticketing service health.

        Returns:
            Tuple of (is_healthy, latency_ms, error_message).
        """
        pass


class KnowledgeServiceInterface(ABC):
    """Interface for knowledge base search."""

    @abstractmethod
    async def search(
        self,
        query: str,
        department: Optional[Department] = None,
        limit: int = 3,
    ) -> list[KnowledgeArticle]:
        """
        Search the knowledge base for relevant articles.

        Args:
            query: Search query.
            department: Optional department filter.
            limit: Maximum number of articles to return.

        Returns:
            List of relevant knowledge articles.
        """
        pass

    @abstractmethod
    async def search_with_content(
        self,
        query: str,
        department: Optional[Department] = None,
        limit: int = 3,
    ) -> tuple[list[KnowledgeArticle], list[dict]]:
        """
        Search the knowledge base and return both article metadata and full content.

        Args:
            query: Search query.
            department: Optional department filter.
            limit: Maximum number of articles to return.

        Returns:
            Tuple of (list of KnowledgeArticle metadata, list of dicts with full content).
            The content dicts include: article_id, title, content, snippet, tags.
        """
        pass

    @abstractmethod
    async def get_article(
        self,
        article_id: str,
    ) -> Optional[KnowledgeArticle]:
        """
        Get a specific article by ID.

        Args:
            article_id: The article identifier.

        Returns:
            KnowledgeArticle if found, None otherwise.
        """
        pass

    @abstractmethod
    async def health_check(self) -> tuple[bool, Optional[int], Optional[str]]:
        """
        Check knowledge base service health.

        Returns:
            Tuple of (is_healthy, latency_ms, error_message).
        """
        pass


class SessionStoreInterface(ABC):
    """Interface for session storage (stateful conversations)."""

    @abstractmethod
    async def create_session(
        self,
        session: Session,
    ) -> None:
        """
        Create a new session.

        Args:
            session: The session object to store.
        """
        pass

    @abstractmethod
    async def get_session(
        self,
        session_id: UUID,
    ) -> Optional[Session]:
        """
        Retrieve a session by ID.

        Args:
            session_id: The session identifier.

        Returns:
            Session if found, None otherwise.
        """
        pass

    @abstractmethod
    async def update_session(
        self,
        session: Session,
    ) -> None:
        """
        Update an existing session.

        Args:
            session: The updated session object.
        """
        pass

    @abstractmethod
    async def get_sessions_by_student(
        self,
        student_id_hash: str,
        limit: int = 10,
    ) -> list[Session]:
        """
        Get all sessions for a student.

        Args:
            student_id_hash: Hashed student identifier.
            limit: Maximum number of sessions to return.

        Returns:
            List of sessions.
        """
        pass

    @abstractmethod
    async def health_check(self) -> tuple[bool, Optional[int], Optional[str]]:
        """
        Check session store health.

        Returns:
            Tuple of (is_healthy, latency_ms, error_message).
        """
        pass


class AuditLogInterface(ABC):
    """Interface for audit logging (compliance and analytics)."""

    @abstractmethod
    async def log_interaction(
        self,
        audit_log: AuditLog,
    ) -> None:
        """
        Record an interaction in the audit log.

        Args:
            audit_log: The audit log entry to store.
        """
        pass

    @abstractmethod
    async def get_logs_by_session(
        self,
        session_id: UUID,
    ) -> list[AuditLog]:
        """
        Get all audit logs for a session.

        Args:
            session_id: The session identifier.

        Returns:
            List of audit log entries.
        """
        pass

    @abstractmethod
    async def get_logs_by_student(
        self,
        student_id_hash: str,
        limit: int = 100,
    ) -> list[AuditLog]:
        """
        Get audit logs for a student.

        Args:
            student_id_hash: Hashed student identifier.
            limit: Maximum number of logs to return.

        Returns:
            List of audit log entries.
        """
        pass

    @abstractmethod
    async def health_check(self) -> tuple[bool, Optional[int], Optional[str]]:
        """
        Check audit log service health.

        Returns:
            Tuple of (is_healthy, latency_ms, error_message).
        """
        pass
