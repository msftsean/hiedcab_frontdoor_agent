"""
Azure OpenAI LLM service for production intent classification and response generation.
"""

import json
import re
import time
from typing import Optional

import httpx

from app.models.enums import Department, IntentCategory, Sentiment
from app.models.schemas import QueryResult
from app.services.interfaces import LLMServiceInterface


class AzureOpenAILLMService(LLMServiceInterface):
    """Production implementation of LLM service using Azure OpenAI."""

    def __init__(
        self,
        endpoint: str,
        api_key: str,
        deployment: str,
        api_version: str = "2024-05-01-preview",
    ) -> None:
        """Initialize Azure OpenAI client."""
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key
        self.deployment = deployment
        self.api_version = api_version
        self._client = httpx.AsyncClient(timeout=30.0)

    async def _call_openai(
        self,
        messages: list[dict],
        max_tokens: int = 1000,
        temperature: float = 0.1,
    ) -> dict:
        """Make a call to Azure OpenAI API."""
        url = f"{self.endpoint}/openai/deployments/{self.deployment}/chat/completions?api-version={self.api_version}"

        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key,
        }

        payload = {
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        response = await self._client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

    def _parse_json_response(self, content: str) -> dict:
        """Parse JSON from LLM response, handling markdown code blocks."""
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", content)
        if json_match:
            content = json_match.group(1).strip()

        # Try to parse as JSON
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Return empty dict if parsing fails
            return {}

    async def classify_intent(
        self,
        message: str,
        conversation_history: Optional[list[dict]] = None,
    ) -> QueryResult:
        """Classify intent using Azure OpenAI GPT-4o."""

        system_prompt = """You are a university support system assistant that classifies student queries.

Analyze the student's message and return a JSON object with:
{
    "intent": "string - specific intent like password_reset, transcript_request, financial_aid_inquiry, facilities_issue, grade_appeal, course_enrollment, parking_permit, general_question, request_human",
    "intent_category": "one of: ACCOUNT_ACCESS, ACADEMIC_RECORDS, FINANCIAL, FACILITIES, ENROLLMENT, STUDENT_SERVICES, POLICY_EXCEPTION, GENERAL_INQUIRY, STATUS_CHECK, HUMAN_REQUEST",
    "department": "one of: IT, HR, REGISTRAR, FINANCIAL_AID, FACILITIES, STUDENT_AFFAIRS, CAMPUS_SAFETY, ESCALATE_TO_HUMAN",
    "confidence": "float 0.0-1.0 indicating how confident you are",
    "entities": {
        "building": "extracted building name if mentioned",
        "course_code": "extracted course code if mentioned",
        "system": "IT system mentioned like Canvas, Outlook, etc.",
        "date": "any date or deadline mentioned"
    },
    "requires_escalation": "boolean - true if: mentions appeal/waiver/refund, Title IX, mental health, threats, or explicitly asks for human",
    "escalation_reason": "if escalation needed: policy_keyword_detected, sensitive_topic, user_requested_human, or null",
    "pii_detected": "boolean - true if SSN, credit card, or other sensitive personal data found",
    "pii_types": ["list of PII types found: ssn, credit_card, phone, email, dob"],
    "sentiment": "one of: NEUTRAL, FRUSTRATED, URGENT, SATISFIED",
    "urgency_indicators": ["list of urgency words found: urgent, asap, emergency, deadline, today, tonight"]
}

Department routing guide:
- IT: password, login, email, WiFi, software, computer issues
- REGISTRAR: transcripts, enrollment verification, grades, graduation
- FINANCIAL_AID: scholarships, grants, loans, tuition payment help
- FACILITIES: building issues, maintenance, room booking, elevators
- STUDENT_AFFAIRS: housing, dining, student organizations, parking
- CAMPUS_SAFETY: safety concerns, lost items, emergencies
- HR: employment, work-study, payroll
- ESCALATE_TO_HUMAN: appeals, refunds, waivers, Title IX, mental health, threats, explicit human request

Always respond with valid JSON only."""

        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history if provided
        if conversation_history:
            for turn in conversation_history[-5:]:  # Last 5 turns for context
                messages.append(turn)

        messages.append({"role": "user", "content": message})

        try:
            response = await self._call_openai(messages, max_tokens=500, temperature=0.1)
            content = response["choices"][0]["message"]["content"]
            data = self._parse_json_response(content)

            # Map string values to enums with defaults
            intent = data.get("intent", "general_question")

            intent_category_str = data.get("intent_category", "GENERAL_INQUIRY")
            try:
                intent_category = IntentCategory(intent_category_str)
            except ValueError:
                intent_category = IntentCategory.GENERAL_INQUIRY

            department_str = data.get("department", "IT")
            try:
                department = Department(department_str)
            except ValueError:
                department = Department.IT

            sentiment_str = data.get("sentiment", "NEUTRAL")
            try:
                sentiment = Sentiment(sentiment_str)
            except ValueError:
                sentiment = Sentiment.NEUTRAL

            return QueryResult(
                intent=intent,
                intent_category=intent_category,
                department_suggestion=department,
                entities=data.get("entities", {}),
                confidence=float(data.get("confidence", 0.85)),
                requires_escalation=data.get("requires_escalation", False),
                pii_detected=data.get("pii_detected", False),
                pii_types=data.get("pii_types", []),
                sentiment=sentiment,
                urgency_indicators=data.get("urgency_indicators", []),
            )

        except Exception as e:
            # Fallback to low confidence general inquiry on error
            return QueryResult(
                intent="general_question",
                intent_category=IntentCategory.GENERAL_INQUIRY,
                department_suggestion=Department.ESCALATE_TO_HUMAN,
                entities={},
                confidence=0.3,
                requires_escalation=True,
                pii_detected=False,
                pii_types=[],
                sentiment=Sentiment.NEUTRAL,
                urgency_indicators=[],
            )

    async def generate_clarification_question(
        self,
        message: str,
        possible_intents: list[str],
    ) -> str:
        """Generate a clarification question using Azure OpenAI."""

        system_prompt = """You are a helpful university support assistant.
Generate a friendly, concise clarification question to help understand what the student needs.
Keep it brief (1-2 sentences) and offer clear options when possible."""

        user_prompt = f"""The student said: "{message}"

This could be about: {', '.join(possible_intents)}

Generate a clarification question to understand what they need."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response = await self._call_openai(messages, max_tokens=150, temperature=0.7)
            return response["choices"][0]["message"]["content"].strip()
        except Exception:
            # Fallback question
            options = ", ".join(possible_intents[:3]).replace("_", " ")
            return f"I want to make sure I help you with the right thing. Are you asking about {options}?"

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
        """Generate a user-friendly response message with self-service info using Azure OpenAI."""

        # Build KB context for the LLM
        kb_context = ""
        if kb_article_contents:
            kb_context = "\n\nKnowledge Base Articles (use these to help the student):\n"
            for i, article in enumerate(kb_article_contents, 1):
                kb_context += f"\n---Article {i}: {article.get('title', 'N/A')}---\n"
                kb_context += f"{article.get('content', article.get('snippet', 'No content available'))}\n"

        system_prompt = """You are a helpful university support assistant. Your goal is to provide IMMEDIATE, ACTIONABLE help to students.

When knowledge base articles are provided:
1. DIRECTLY answer the student's question using the KB article content
2. Provide step-by-step instructions if available in the articles
3. Include relevant links, phone numbers, or deadlines from the articles
4. Be specific and helpful - don't just say "review the articles below"

If a ticket was created, mention it briefly at the end as a reference number.
If escalated to human, explain that a staff member will follow up.

Keep the response friendly, concise (3-5 sentences), and focused on solving their problem immediately."""

        user_prompt = f"""Student's question: {original_message or intent.replace('_', ' ')}

Issue type: {intent.replace('_', ' ')}
Department: {department.value}
Ticket ID: {ticket_id or 'Not created'}
Escalated to human: {escalated}
Expected response time: {estimated_response_time}
{kb_context}

Provide a helpful response that directly addresses the student's question using the knowledge base information. If KB articles contain step-by-step instructions, include them. Be specific and actionable."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response = await self._call_openai(messages, max_tokens=500, temperature=0.7)
            return response["choices"][0]["message"]["content"].strip()
        except Exception:
            # Fallback message
            dept_names = {
                Department.IT: "IT Support",
                Department.HR: "Human Resources",
                Department.REGISTRAR: "the Registrar's Office",
                Department.FINANCIAL_AID: "Financial Aid",
                Department.FACILITIES: "Facilities Management",
                Department.STUDENT_AFFAIRS: "Student Affairs",
                Department.CAMPUS_SAFETY: "Campus Safety",
                Department.ESCALATE_TO_HUMAN: "a support specialist",
            }
            dept_name = dept_names.get(department, department.value)

            if escalated:
                return f"I've forwarded your request to {dept_name} for personal attention. A team member will reach out within {estimated_response_time}. Your reference number is {ticket_id}."
            elif ticket_id:
                return f"I've created ticket {ticket_id} and routed it to {dept_name}. You can expect a response within {estimated_response_time}."
            else:
                return f"I've found some helpful information from {dept_name}. Please review the articles below."

    async def health_check(self) -> tuple[bool, Optional[int], Optional[str]]:
        """Check Azure OpenAI service health."""
        start_time = time.time()

        try:
            messages = [{"role": "user", "content": "ping"}]
            await self._call_openai(messages, max_tokens=5, temperature=0)
            latency_ms = int((time.time() - start_time) * 1000)
            return True, latency_ms, None
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            return False, latency_ms, str(e)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
