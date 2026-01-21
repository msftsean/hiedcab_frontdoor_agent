"""
Shared enumerations for the Front Door Support Agent.
Matches the data model specification.
"""

from enum import Enum


class Department(str, Enum):
    """Target departments for routing support requests."""
    IT = "IT"
    HR = "HR"
    REGISTRAR = "REGISTRAR"
    FINANCIAL_AID = "FINANCIAL_AID"
    FACILITIES = "FACILITIES"
    STUDENT_AFFAIRS = "STUDENT_AFFAIRS"
    CAMPUS_SAFETY = "CAMPUS_SAFETY"
    ESCALATE_TO_HUMAN = "ESCALATE_TO_HUMAN"


class Priority(str, Enum):
    """Priority levels for support requests."""
    LOW = "LOW"        # Standard request, no urgency
    MEDIUM = "MEDIUM"  # Normal priority
    HIGH = "HIGH"      # Urgency indicators or frustrated sentiment
    URGENT = "URGENT"  # Sensitive topics, safety concerns


class Sentiment(str, Enum):
    """Detected sentiment from user queries."""
    NEUTRAL = "NEUTRAL"
    FRUSTRATED = "FRUSTRATED"
    URGENT = "URGENT"
    SATISFIED = "SATISFIED"


class ActionStatus(str, Enum):
    """Outcome status of the ActionAgent's execution."""
    CREATED = "created"                        # Ticket created successfully
    ESCALATED = "escalated"                    # Routed to human reviewer
    PENDING_CLARIFICATION = "pending_clarification"  # Awaiting user clarification
    KB_ONLY = "kb_only"                        # No ticket created, KB articles provided
    ERROR = "error"                            # Processing error occurred


class EscalationReason(str, Enum):
    """Reasons for escalating to human review."""
    CONFIDENCE_TOO_LOW = "confidence_too_low"                    # confidence < 0.70
    POLICY_KEYWORD_DETECTED = "policy_keyword_detected"          # appeal, waiver, refund, etc.
    SENSITIVE_TOPIC = "sensitive_topic"                          # Title IX, mental health, threats
    MULTI_DEPARTMENT = "multi_department"                        # Requires coordination
    USER_REQUESTED_HUMAN = "user_requested_human"                # Explicit human request
    MAX_CLARIFICATIONS_EXCEEDED = "max_clarifications_exceeded"  # 3 failed disambiguation attempts


class IntentCategory(str, Enum):
    """Categories for grouping detected intents."""
    ACCOUNT_ACCESS = "ACCOUNT_ACCESS"        # password_reset, login_issues, account_locked
    ACADEMIC_RECORDS = "ACADEMIC_RECORDS"    # transcript_request, grade_inquiry, enrollment_verification
    FINANCIAL = "FINANCIAL"                  # financial_aid_inquiry, tuition_payment, refund_request
    FACILITIES = "FACILITIES"                # facilities_issue, maintenance_request, room_booking
    ENROLLMENT = "ENROLLMENT"                # course_enrollment, add_drop, registration_hold
    STUDENT_SERVICES = "STUDENT_SERVICES"    # parking_permit, id_card, housing
    POLICY_EXCEPTION = "POLICY_EXCEPTION"    # grade_appeal, withdrawal_request, waiver_request
    GENERAL_INQUIRY = "GENERAL_INQUIRY"      # general_question, department_contact
    STATUS_CHECK = "STATUS_CHECK"            # ticket_status, request_followup
    HUMAN_REQUEST = "HUMAN_REQUEST"          # request_human, speak_to_person


class TicketStatus(str, Enum):
    """Status values for support tickets."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING_INFO = "pending_info"
    RESOLVED = "resolved"
    CLOSED = "closed"
