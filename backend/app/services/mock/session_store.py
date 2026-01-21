"""
Mock session store for testing and demo mode.
Stores sessions in memory.
"""

from typing import Optional
from uuid import UUID

from app.models.schemas import Session
from app.services.interfaces import SessionStoreInterface


class MockSessionStore(SessionStoreInterface):
    """Mock implementation of session storage using in-memory dict."""

    # Class-level storage to persist across requests
    _sessions: dict[str, Session] = {}

    async def create_session(
        self,
        session: Session,
    ) -> None:
        """Store a new session in memory."""
        key = str(session.session_id)
        MockSessionStore._sessions[key] = session

    async def get_session(
        self,
        session_id: UUID,
    ) -> Optional[Session]:
        """Retrieve a session from memory."""
        key = str(session_id)
        return MockSessionStore._sessions.get(key)

    async def update_session(
        self,
        session: Session,
    ) -> None:
        """Update a session in memory."""
        key = str(session.session_id)
        MockSessionStore._sessions[key] = session

    async def get_sessions_by_student(
        self,
        student_id_hash: str,
        limit: int = 10,
    ) -> list[Session]:
        """Get all sessions for a student."""
        student_sessions = [
            s for s in MockSessionStore._sessions.values()
            if s.student_id_hash == student_id_hash
        ]

        # Sort by last_active descending
        student_sessions.sort(key=lambda s: s.last_active, reverse=True)

        return student_sessions[:limit]

    async def health_check(self) -> tuple[bool, Optional[int], Optional[str]]:
        """Mock health check - always healthy."""
        return True, 2, None

    @classmethod
    def clear_all(cls) -> None:
        """Clear all sessions (for testing)."""
        cls._sessions.clear()
