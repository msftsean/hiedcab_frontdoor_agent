"""
Mock audit log service for testing and demo mode.
Stores audit logs in memory.
"""

from typing import Optional
from uuid import UUID

from app.models.schemas import AuditLog
from app.services.interfaces import AuditLogInterface


class MockAuditLog(AuditLogInterface):
    """Mock implementation of audit logging using in-memory storage."""

    # Class-level storage to persist across requests
    _logs: list[AuditLog] = []

    async def log_interaction(
        self,
        audit_log: AuditLog,
    ) -> None:
        """Record an interaction in memory."""
        MockAuditLog._logs.append(audit_log)

    async def get_logs_by_session(
        self,
        session_id: UUID,
    ) -> list[AuditLog]:
        """Get all audit logs for a session."""
        session_str = str(session_id)
        return [
            log for log in MockAuditLog._logs
            if str(log.session_id) == session_str
        ]

    async def get_logs_by_student(
        self,
        student_id_hash: str,
        limit: int = 100,
    ) -> list[AuditLog]:
        """Get audit logs for a student."""
        student_logs = [
            log for log in MockAuditLog._logs
            if log.student_id_hash == student_id_hash
        ]

        # Sort by timestamp descending
        student_logs.sort(key=lambda l: l.timestamp, reverse=True)

        return student_logs[:limit]

    async def health_check(self) -> tuple[bool, Optional[int], Optional[str]]:
        """Mock health check - always healthy."""
        return True, 1, None

    @classmethod
    def clear_all(cls) -> None:
        """Clear all logs (for testing)."""
        cls._logs.clear()

    @classmethod
    def get_all_logs(cls) -> list[AuditLog]:
        """Get all logs (for testing/debugging)."""
        return cls._logs.copy()
