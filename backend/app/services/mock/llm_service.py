"""
Mock LLM service for testing and demo mode.
Uses pattern matching and the intent examples data to classify intents.
"""

import json
import re
from pathlib import Path
from typing import Optional

from app.models.enums import Department, IntentCategory, Sentiment
from app.models.schemas import QueryResult
from app.services.interfaces import LLMServiceInterface


class MockLLMService(LLMServiceInterface):
    """Mock implementation of LLM service using pattern matching."""

    def __init__(self) -> None:
        """Initialize with intent examples from mock data."""
        self._intent_data = self._load_intent_data()
        self._policy_keywords = self._intent_data.get("policy_keywords", [])
        self._sensitive_topics = self._intent_data.get("sensitive_topics", [])
        self._urgency_indicators = self._intent_data.get("urgency_indicators", [])

    def _load_intent_data(self) -> dict:
        """Load intent examples from mock data file."""
        mock_data_path = Path(__file__).parent.parent.parent.parent / "mock_data" / "intent_examples.json"
        if mock_data_path.exists():
            with open(mock_data_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"intent_examples": {}}

    def _detect_pii(self, message: str) -> tuple[bool, list[str]]:
        """Detect potential PII in message."""
        pii_types = []
        lower_message = message.lower()

        # Social Security Number pattern
        if re.search(r"\b\d{3}-\d{2}-\d{4}\b", message):
            pii_types.append("ssn")

        # Email pattern
        if re.search(r"\b[\w.-]+@[\w.-]+\.\w+\b", message):
            pii_types.append("email")

        # Phone number pattern
        if re.search(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", message):
            pii_types.append("phone")

        # Credit card pattern
        if re.search(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", message):
            pii_types.append("credit_card")

        # Date of birth indicators
        if any(term in lower_message for term in ["born on", "birthday", "date of birth", "dob"]):
            pii_types.append("dob")

        return len(pii_types) > 0, pii_types

    def _detect_sentiment(self, message: str) -> Sentiment:
        """Detect sentiment from message."""
        lower_message = message.lower()

        # Frustrated indicators
        frustrated_terms = [
            "frustrated", "annoyed", "angry", "terrible", "awful",
            "ridiculous", "unacceptable", "disappointed", "upset",
            "not working", "broken", "failed", "can't believe",
            "this is crazy", "waste of time"
        ]
        if any(term in lower_message for term in frustrated_terms):
            return Sentiment.FRUSTRATED

        # Urgent indicators
        if any(term in lower_message for term in self._urgency_indicators):
            return Sentiment.URGENT

        # Satisfied indicators
        satisfied_terms = ["thank you", "thanks", "great", "perfect", "excellent", "helpful"]
        if any(term in lower_message for term in satisfied_terms):
            return Sentiment.SATISFIED

        return Sentiment.NEUTRAL

    def _find_urgency_indicators(self, message: str) -> list[str]:
        """Find urgency indicators in message."""
        lower_message = message.lower()
        found = []
        for indicator in self._urgency_indicators:
            if indicator in lower_message:
                found.append(indicator)
        return found

    def _check_escalation_required(self, message: str) -> tuple[bool, Optional[str]]:
        """Check if message requires escalation."""
        lower_message = message.lower()

        # Check for policy keywords
        for keyword in self._policy_keywords:
            if keyword in lower_message:
                return True, "policy_keyword_detected"

        # Check for sensitive topics
        for topic in self._sensitive_topics:
            if topic in lower_message:
                return True, "sensitive_topic"

        # Check for explicit human request
        human_request_terms = [
            "talk to a person", "speak to someone", "human please",
            "real person", "talk to human", "connect me to",
            "transfer me", "speak to a human", "live agent"
        ]
        if any(term in lower_message for term in human_request_terms):
            return True, "user_requested_human"

        return False, None

    def _extract_entities(self, message: str, intent: str) -> dict:
        """Extract entities from message based on intent."""
        entities = {}
        lower_message = message.lower()

        # Building names (common campus buildings)
        buildings = ["smith hall", "johnson center", "library", "student union", "dorm"]
        for building in buildings:
            if building in lower_message:
                entities["building"] = building.title()
                break

        # Course codes (pattern: 2-4 letters followed by 3-4 digits)
        course_match = re.search(r"\b([A-Z]{2,4})\s*(\d{3,4})\b", message, re.IGNORECASE)
        if course_match:
            entities["course_code"] = f"{course_match.group(1).upper()}{course_match.group(2)}"

        # System names
        systems = ["canvas", "blackboard", "banner", "workday", "outlook", "vpn"]
        for system in systems:
            if system in lower_message:
                entities["system"] = system.title()
                break

        return entities

    def _match_intent(self, message: str) -> tuple[str, IntentCategory, Department, float]:
        """Match message to intent using pattern matching."""
        lower_message = message.lower()
        intent_examples = self._intent_data.get("intent_examples", {})

        best_match = None
        best_score = 0.0

        for intent_name, intent_info in intent_examples.items():
            examples = intent_info.get("examples", [])
            for example in examples:
                example_lower = example.lower()
                # Simple word overlap scoring
                example_words = set(example_lower.split())
                message_words = set(lower_message.split())
                overlap = len(example_words & message_words)
                score = overlap / max(len(example_words), 1)

                # Boost score for exact substring match
                if example_lower in lower_message or lower_message in example_lower:
                    score = max(score, 0.85)

                if score > best_score:
                    best_score = score
                    best_match = (
                        intent_name,
                        IntentCategory(intent_info.get("category", "GENERAL_INQUIRY")),
                        Department(intent_info.get("department", "IT")),
                    )

        if best_match and best_score >= 0.3:
            # Scale confidence based on match quality
            confidence = min(0.95, 0.5 + best_score * 0.5)
            return best_match[0], best_match[1], best_match[2], confidence

        # Default to general inquiry with low confidence
        return "general_question", IntentCategory.GENERAL_INQUIRY, Department.IT, 0.45

    async def classify_intent(
        self,
        message: str,
        conversation_history: Optional[list[dict]] = None,
    ) -> QueryResult:
        """Classify intent using pattern matching."""
        # Detect PII
        pii_detected, pii_types = self._detect_pii(message)

        # Detect sentiment
        sentiment = self._detect_sentiment(message)

        # Find urgency indicators
        urgency_indicators = self._find_urgency_indicators(message)

        # Check for escalation
        requires_escalation, escalation_reason = self._check_escalation_required(message)

        # Match intent
        intent, intent_category, department, confidence = self._match_intent(message)

        # Extract entities
        entities = self._extract_entities(message, intent)

        # Override department if escalation required
        if requires_escalation:
            department = Department.ESCALATE_TO_HUMAN

        return QueryResult(
            intent=intent,
            intent_category=intent_category,
            department_suggestion=department,
            entities=entities,
            confidence=confidence,
            requires_escalation=requires_escalation,
            pii_detected=pii_detected,
            pii_types=pii_types,
            sentiment=sentiment,
            urgency_indicators=urgency_indicators,
        )

    async def generate_clarification_question(
        self,
        message: str,
        possible_intents: list[str],
    ) -> str:
        """Generate a clarification question."""
        # Map intents to human-readable options
        intent_descriptions = {
            "password_reset": "password reset for a university system",
            "login_issues": "login problems with your account",
            "financial_aid_inquiry": "financial aid or scholarships",
            "tuition_payment": "tuition payments or billing",
            "transcript_request": "requesting academic transcripts",
            "enrollment_verification": "enrollment verification letters",
            "facilities_issue": "facilities or maintenance issues",
            "course_enrollment": "course registration",
            "general_question": "general university information",
        }

        options = []
        for intent in possible_intents[:3]:  # Limit to 3 options
            desc = intent_descriptions.get(intent, intent.replace("_", " "))
            options.append(desc)

        if len(options) == 1:
            return f"Just to clarify, are you asking about {options[0]}?"
        elif len(options) == 2:
            return f"I want to make sure I understand. Are you asking about {options[0]} or {options[1]}?"
        else:
            return f"I want to help you with the right issue. Are you asking about {options[0]}, {options[1]}, or {options[2]}?"

    async def generate_response_message(
        self,
        intent: str,
        department: Department,
        ticket_id: Optional[str],
        escalated: bool,
        estimated_response_time: str,
        original_message: Optional[str] = None,
        knowledge_articles: Optional[list] = None,
        kb_article_contents: Optional[list[dict]] = None,
    ) -> str:
        """Generate a user-friendly response message with self-service info."""
        dept_names = {
            Department.IT: "IT Support",
            Department.HR: "Human Resources",
            Department.REGISTRAR: "the Registrar's Office",
            Department.FINANCIAL_AID: "Financial Aid",
            Department.FACILITIES: "Facilities Management",
            Department.STUDENT_AFFAIRS: "Student Affairs",
            Department.CAMPUS_SAFETY: "Campus Safety",
            Department.ESCALATE_TO_HUMAN: "a human support specialist",
        }

        dept_name = dept_names.get(department, str(department.value))

        # Build self-service content from KB articles if available
        self_service_info = ""
        if kb_article_contents:
            # Use the first/most relevant article's content for self-service
            top_article = kb_article_contents[0]
            content = top_article.get("content", top_article.get("snippet", ""))
            if content:
                self_service_info = f"\n\nHere's how you can resolve this:\n{content}"

        if escalated:
            return (
                f"I've forwarded your request to {dept_name} for personal attention. "
                f"A team member will reach out to you within {estimated_response_time}. "
                f"Your reference number is {ticket_id}."
            )

        if ticket_id:
            base_msg = (
                f"I've created a support ticket ({ticket_id}) and routed it to {dept_name}. "
                f"You can expect a response within {estimated_response_time}."
            )
            if self_service_info:
                return base_msg + self_service_info + "\n\nLet me know if you need additional assistance."
            return base_msg + " Is there anything else I can help you with?"

        if self_service_info:
            return (
                f"I've found some helpful information from {dept_name}."
                f"{self_service_info}\n\n"
                "Let me know if you need additional assistance."
            )

        return (
            f"I've found some helpful information from {dept_name}. "
            "Please review the articles below. Let me know if you need additional assistance."
        )

    async def health_check(self) -> tuple[bool, Optional[int], Optional[str]]:
        """Mock health check - always healthy."""
        return True, 5, None
