"""
Mock ticket service for testing and demo mode.
Stores tickets in memory and loads sample data.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from app.models.enums import Department, Priority, TicketStatus
from app.models.schemas import TicketStatusResponse, TicketSummary
from app.services.interfaces import TicketServiceInterface


class MockTicketService(TicketServiceInterface):
    """Mock implementation of ticket service using in-memory storage."""

    # Class-level storage to persist across requests
    _tickets: dict[str, dict] = {}
    _ticket_counter: dict[str, int] = {}
    _initialized: bool = False

    def __init__(self) -> None:
        """Initialize and load sample tickets if not already done."""
        if not MockTicketService._initialized:
            self._load_sample_tickets()
            MockTicketService._initialized = True

    def _load_sample_tickets(self) -> None:
        """Load sample tickets from mock data file."""
        mock_data_path = Path(__file__).parent.parent.parent.parent / "mock_data" / "sample_tickets.json"
        if mock_data_path.exists():
            with open(mock_data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for ticket in data.get("tickets", []):
                    ticket_id = ticket["ticket_id"]
                    MockTicketService._tickets[ticket_id] = ticket

                    # Initialize counter based on existing tickets
                    parts = ticket_id.split("-")
                    if len(parts) == 4:
                        dept = parts[1]
                        date_str = parts[2]
                        seq = int(parts[3])
                        key = f"{dept}-{date_str}"
                        MockTicketService._ticket_counter[key] = max(
                            MockTicketService._ticket_counter.get(key, 0),
                            seq
                        )

    def _generate_ticket_id(self, department: Department) -> str:
        """Generate a new ticket ID in format TKT-{DEPT}-{YYYYMMDD}-{SEQ}."""
        today = datetime.now(timezone.utc).strftime("%Y%m%d")

        # Get department code (2-3 letters)
        dept_codes = {
            Department.IT: "IT",
            Department.HR: "HR",
            Department.REGISTRAR: "REG",
            Department.FINANCIAL_AID: "FIN",
            Department.FACILITIES: "FAC",
            Department.STUDENT_AFFAIRS: "STU",
            Department.CAMPUS_SAFETY: "SAF",
            Department.ESCALATE_TO_HUMAN: "ESC",
        }
        dept_code = dept_codes.get(department, "GEN")

        # Increment counter
        key = f"{dept_code}-{today}"
        MockTicketService._ticket_counter[key] = MockTicketService._ticket_counter.get(key, 0) + 1
        seq = MockTicketService._ticket_counter[key]

        return f"TKT-{dept_code}-{today}-{seq:04d}"

    async def create_ticket(
        self,
        department: Department,
        priority: Priority,
        summary: str,
        description: str,
        student_id_hash: str,
        entities: Optional[dict] = None,
    ) -> tuple[str, str]:
        """Create a new ticket in memory."""
        ticket_id = self._generate_ticket_id(department)
        now = datetime.now(timezone.utc).isoformat()

        ticket = {
            "ticket_id": ticket_id,
            "department": department.value,
            "status": TicketStatus.OPEN.value,
            "priority": priority.value,
            "summary": summary[:200],  # Truncate summary
            "description": description,
            "created_at": now,
            "updated_at": now,
            "assigned_to": None,
            "student_id_hash": student_id_hash,
            "resolution_summary": None,
            "entities": entities or {},
        }

        MockTicketService._tickets[ticket_id] = ticket

        # Generate mock URL
        ticket_url = f"https://servicenow.university.edu/ticket/{ticket_id}"

        return ticket_id, ticket_url

    async def get_ticket_status(
        self,
        ticket_id: str,
    ) -> Optional[TicketStatusResponse]:
        """Get ticket status from memory."""
        ticket = MockTicketService._tickets.get(ticket_id)
        if not ticket:
            return None

        return TicketStatusResponse(
            ticket_id=ticket["ticket_id"],
            department=Department(ticket["department"]),
            status=TicketStatus(ticket["status"]),
            priority=Priority(ticket["priority"]) if ticket.get("priority") else None,
            summary=ticket.get("summary"),
            description=ticket.get("description"),
            created_at=datetime.fromisoformat(ticket["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(ticket["updated_at"].replace("Z", "+00:00")) if ticket.get("updated_at") else None,
            assigned_to=ticket.get("assigned_to"),
            resolution_summary=ticket.get("resolution_summary"),
        )

    async def list_user_tickets(
        self,
        student_id_hash: str,
        status_filter: Optional[str] = None,
        limit: int = 10,
    ) -> list[TicketSummary]:
        """List tickets for a user from memory."""
        user_tickets = []

        for ticket in MockTicketService._tickets.values():
            if ticket.get("student_id_hash") == student_id_hash:
                if status_filter and ticket.get("status") != status_filter:
                    continue
                user_tickets.append(ticket)

        # Sort by created_at descending
        user_tickets.sort(key=lambda t: t.get("created_at", ""), reverse=True)

        # Limit results
        user_tickets = user_tickets[:limit]

        return [
            TicketSummary(
                ticket_id=t["ticket_id"],
                department=Department(t["department"]),
                status=t["status"],
                created_at=datetime.fromisoformat(t["created_at"].replace("Z", "+00:00")),
                summary=t.get("summary", "No summary available"),
                description=t.get("description"),
            )
            for t in user_tickets
        ]

    # =========================================================================
    # Admin Methods
    # =========================================================================

    async def list_all_tickets(
        self,
        status_filter: Optional[str] = None,
        department_filter: Optional[Department] = None,
        limit: int = 50,
    ) -> list[TicketSummary]:
        """List all tickets (admin view)."""
        all_tickets = []

        for ticket in MockTicketService._tickets.values():
            # Apply status filter
            if status_filter and ticket.get("status") != status_filter:
                continue

            # Apply department filter
            if department_filter and ticket.get("department") != department_filter.value:
                continue

            all_tickets.append(ticket)

        # Sort by created_at descending (newest first)
        all_tickets.sort(key=lambda t: t.get("created_at", ""), reverse=True)

        # Limit results
        all_tickets = all_tickets[:limit]

        return [
            TicketSummary(
                ticket_id=t["ticket_id"],
                department=Department(t["department"]),
                status=t["status"],
                created_at=datetime.fromisoformat(t["created_at"].replace("Z", "+00:00")),
                summary=t.get("summary", "No summary available"),
                description=t.get("description"),
            )
            for t in all_tickets
        ]

    async def update_ticket_status(
        self,
        ticket_id: str,
        new_status: TicketStatus,
        assigned_to: Optional[str] = None,
        resolution_summary: Optional[str] = None,
    ) -> Optional[TicketStatusResponse]:
        """Update ticket status (admin/triage action)."""
        ticket = MockTicketService._tickets.get(ticket_id)
        if not ticket:
            return None

        # Update fields
        ticket["status"] = new_status.value
        ticket["updated_at"] = datetime.now(timezone.utc).isoformat()

        if assigned_to is not None:
            ticket["assigned_to"] = assigned_to

        if resolution_summary is not None:
            ticket["resolution_summary"] = resolution_summary

        return TicketStatusResponse(
            ticket_id=ticket["ticket_id"],
            department=Department(ticket["department"]),
            status=TicketStatus(ticket["status"]),
            priority=Priority(ticket["priority"]) if ticket.get("priority") else None,
            summary=ticket.get("summary"),
            description=ticket.get("description"),
            created_at=datetime.fromisoformat(ticket["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(ticket["updated_at"].replace("Z", "+00:00")),
            assigned_to=ticket.get("assigned_to"),
            resolution_summary=ticket.get("resolution_summary"),
        )

    async def delete_ticket(
        self,
        ticket_id: str,
    ) -> bool:
        """Delete a ticket (admin action)."""
        if ticket_id in MockTicketService._tickets:
            del MockTicketService._tickets[ticket_id]
            return True
        return False

    async def health_check(self) -> tuple[bool, Optional[int], Optional[str]]:
        """Mock health check - always healthy."""
        return True, 10, None
