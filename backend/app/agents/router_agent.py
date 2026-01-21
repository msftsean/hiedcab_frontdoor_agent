"""
RouterAgent: Routing decisions and escalation logic.

Bounded Authority:
- CAN: Determine department, set priority, trigger escalation based on rules
- CANNOT: Create tickets, modify data, access external systems
"""

from app.core.config import Settings
from app.models.enums import (
    Department,
    EscalationReason,
    IntentCategory,
    Priority,
    Sentiment,
)
from app.models.schemas import QueryResult, RoutingDecision


class RouterAgent:
    """
    Agent responsible for routing decisions.

    Takes QueryResult and applies business rules to determine:
    - Target department
    - Priority level
    - Whether human escalation is needed
    - Expected SLA
    """

    # Department mappings based on intent category
    CATEGORY_TO_DEPARTMENT: dict[IntentCategory, Department] = {
        IntentCategory.ACCOUNT_ACCESS: Department.IT,
        IntentCategory.ACADEMIC_RECORDS: Department.REGISTRAR,
        IntentCategory.FINANCIAL: Department.FINANCIAL_AID,
        IntentCategory.FACILITIES: Department.FACILITIES,
        IntentCategory.ENROLLMENT: Department.REGISTRAR,
        IntentCategory.STUDENT_SERVICES: Department.STUDENT_AFFAIRS,
        IntentCategory.POLICY_EXCEPTION: Department.STUDENT_AFFAIRS,
        IntentCategory.GENERAL_INQUIRY: Department.IT,
        IntentCategory.STATUS_CHECK: Department.IT,
        IntentCategory.HUMAN_REQUEST: Department.ESCALATE_TO_HUMAN,
    }

    # Intents that always require human review
    ESCALATION_INTENTS: set[str] = {
        "grade_appeal",
        "withdrawal_request",
        "waiver_request",
        "refund_request",
        "request_human",
        "speak_to_person",
    }

    def __init__(self, settings: Settings) -> None:
        """
        Initialize RouterAgent with settings.

        Args:
            settings: Application settings for thresholds and SLAs.
        """
        self._settings = settings

    def route(
        self,
        query_result: QueryResult,
        clarification_attempts: int = 0,
    ) -> RoutingDecision:
        """
        Determine routing for a query.

        Args:
            query_result: Output from QueryAgent analysis.
            clarification_attempts: Number of clarification attempts so far.

        Returns:
            RoutingDecision with department, priority, and escalation info.
        """
        rules_applied: list[str] = []

        # Start with suggested department from QueryAgent
        department = query_result.department_suggestion
        rules_applied.append("query_agent_suggestion")

        # Override based on intent category if needed
        if query_result.intent_category in self.CATEGORY_TO_DEPARTMENT:
            dept_from_category = self.CATEGORY_TO_DEPARTMENT[query_result.intent_category]
            if dept_from_category != department:
                department = dept_from_category
                rules_applied.append("category_to_department_mapping")

        # Determine priority
        priority = self._determine_priority(query_result)
        rules_applied.append(f"priority_{priority.value.lower()}")

        # Check escalation conditions
        escalate, reason = self._check_escalation(
            query_result=query_result,
            clarification_attempts=clarification_attempts,
        )

        if escalate:
            rules_applied.append(f"escalation_{reason.value}")
            department = Department.ESCALATE_TO_HUMAN

        # Calculate SLA based on priority
        sla_hours = self._get_sla_hours(priority)
        rules_applied.append(f"sla_{sla_hours}h")

        return RoutingDecision(
            department=department,
            priority=priority,
            escalate_to_human=escalate,
            escalation_reason=reason if escalate else None,
            suggested_sla_hours=sla_hours,
            routing_rules_applied=rules_applied,
        )

    def _determine_priority(self, query_result: QueryResult) -> Priority:
        """Determine priority based on query analysis."""
        # Urgent: sensitive topics or safety concerns
        if query_result.requires_escalation:
            return Priority.URGENT

        # High: frustrated sentiment or urgency indicators
        if query_result.sentiment == Sentiment.FRUSTRATED:
            return Priority.HIGH

        if query_result.sentiment == Sentiment.URGENT:
            return Priority.HIGH

        if query_result.urgency_indicators:
            return Priority.HIGH

        # Medium: standard requests with good confidence
        if query_result.confidence >= self._settings.confidence_threshold:
            return Priority.MEDIUM

        # Low: general inquiries
        if query_result.intent_category == IntentCategory.GENERAL_INQUIRY:
            return Priority.LOW

        return Priority.MEDIUM

    def _check_escalation(
        self,
        query_result: QueryResult,
        clarification_attempts: int,
    ) -> tuple[bool, EscalationReason | None]:
        """Check if escalation to human is required."""
        # Already flagged by QueryAgent
        if query_result.requires_escalation:
            # Determine specific reason
            if query_result.intent_category == IntentCategory.HUMAN_REQUEST:
                return True, EscalationReason.USER_REQUESTED_HUMAN

            if query_result.intent_category == IntentCategory.POLICY_EXCEPTION:
                return True, EscalationReason.POLICY_KEYWORD_DETECTED

            return True, EscalationReason.SENSITIVE_TOPIC

        # Check for explicit human request intent
        if query_result.intent in self.ESCALATION_INTENTS:
            if query_result.intent in ("request_human", "speak_to_person"):
                return True, EscalationReason.USER_REQUESTED_HUMAN
            return True, EscalationReason.POLICY_KEYWORD_DETECTED

        # Low confidence requires clarification or escalation
        if query_result.confidence < self._settings.confidence_threshold:
            if clarification_attempts >= self._settings.max_clarification_attempts:
                return True, EscalationReason.MAX_CLARIFICATIONS_EXCEEDED
            # Don't escalate yet - will ask for clarification
            return False, None

        return False, None

    def _get_sla_hours(self, priority: Priority) -> int:
        """Get SLA hours based on priority."""
        sla_map = {
            Priority.URGENT: self._settings.sla_urgent_hours,
            Priority.HIGH: self._settings.sla_high_hours,
            Priority.MEDIUM: self._settings.sla_medium_hours,
            Priority.LOW: self._settings.sla_low_hours,
        }
        return sla_map.get(priority, self._settings.sla_medium_hours)

    def needs_clarification(
        self,
        query_result: QueryResult,
        clarification_attempts: int,
    ) -> bool:
        """
        Check if clarification is needed before routing.

        Args:
            query_result: Output from QueryAgent analysis.
            clarification_attempts: Number of attempts so far.

        Returns:
            True if clarification should be requested.
        """
        # Don't ask for clarification if already at max attempts
        if clarification_attempts >= self._settings.max_clarification_attempts:
            return False

        # Don't ask if escalation is already required
        if query_result.requires_escalation:
            return False

        # Request clarification if confidence is too low
        return query_result.confidence < self._settings.confidence_threshold
