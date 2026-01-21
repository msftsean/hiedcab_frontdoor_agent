"""
QueryAgent: Intent detection and entity extraction.

Bounded Authority:
- CAN: Analyze text, detect intent, extract entities, detect PII, assess sentiment
- CANNOT: Create tickets, access knowledge base, make routing decisions
"""

from typing import Optional

from app.models.schemas import QueryResult, ConversationTurn
from app.services.interfaces import LLMServiceInterface


class QueryAgent:
    """
    Agent responsible for understanding user queries.

    Takes raw user input and produces structured QueryResult with:
    - Detected intent and category
    - Extracted entities (buildings, courses, systems, etc.)
    - Confidence score
    - PII detection flags
    - Sentiment analysis
    - Urgency indicators
    """

    def __init__(self, llm_service: LLMServiceInterface) -> None:
        """
        Initialize QueryAgent with LLM service.

        Args:
            llm_service: LLM service for intent classification.
        """
        self._llm = llm_service

    async def analyze(
        self,
        message: str,
        conversation_history: Optional[list[ConversationTurn]] = None,
    ) -> QueryResult:
        """
        Analyze a user message to detect intent and extract information.

        Args:
            message: The user's support query.
            conversation_history: Previous conversation turns for context.

        Returns:
            QueryResult with intent, entities, confidence, and metadata.
        """
        # Convert conversation history to format expected by LLM
        history_dicts = None
        if conversation_history:
            history_dicts = [
                {
                    "turn_number": turn.turn_number,
                    "intent": turn.intent,
                    "timestamp": turn.timestamp.isoformat(),
                }
                for turn in conversation_history
            ]

        # Use LLM service for classification
        result = await self._llm.classify_intent(
            message=message,
            conversation_history=history_dicts,
        )

        return result

    async def generate_clarification(
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
        return await self._llm.generate_clarification_question(
            message=message,
            possible_intents=possible_intents,
        )
