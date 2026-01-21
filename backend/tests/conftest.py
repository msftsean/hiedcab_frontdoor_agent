"""
Pytest configuration and shared fixtures for the Front Door Support Agent.
"""

import os
import pytest
from datetime import datetime, timezone
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

# Set test environment before importing app modules
os.environ["ENVIRONMENT"] = "test"
os.environ["MOCK_MODE"] = "true"

from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Use asyncio for async tests."""
    return "asyncio"


@pytest.fixture
def mock_session_id() -> str:
    """Generate a mock session ID."""
    return str(uuid4())


@pytest.fixture
def mock_student_id_hash() -> str:
    """Generate a mock hashed student ID."""
    import hashlib
    return hashlib.sha256(b"test_student_123").hexdigest()


@pytest.fixture
def mock_ticket_id() -> str:
    """Generate a mock ticket ID in the expected format."""
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"TKT-IT-{today}-0001"


@pytest.fixture
def sample_chat_request() -> dict:
    """Sample chat request for testing."""
    return {
        "message": "I forgot my password and can't log into Canvas",
        "session_id": None
    }


@pytest.fixture
def sample_chat_request_with_session(mock_session_id: str) -> dict:
    """Sample chat request with existing session."""
    return {
        "message": "What's the status of my ticket?",
        "session_id": mock_session_id
    }


@pytest.fixture
def sample_ambiguous_request() -> dict:
    """Sample ambiguous chat request for clarification testing."""
    return {
        "message": "I need help with my account",
        "session_id": None
    }


@pytest.fixture
def sample_escalation_request() -> dict:
    """Sample request that should trigger escalation."""
    return {
        "message": "I want to appeal my grade in CS101",
        "session_id": None
    }


@pytest.fixture
def sample_human_request() -> dict:
    """Sample request for human assistance."""
    return {
        "message": "I need to talk to a real person",
        "session_id": None
    }


@pytest.fixture
def sample_query_result() -> dict:
    """Sample QueryAgent output."""
    return {
        "intent": "password_reset",
        "intent_category": "ACCOUNT_ACCESS",
        "department_suggestion": "IT",
        "entities": {"system": "Canvas"},
        "confidence": 0.92,
        "requires_escalation": False,
        "pii_detected": False,
        "pii_types": [],
        "sentiment": "NEUTRAL",
        "urgency_indicators": []
    }


@pytest.fixture
def sample_routing_decision() -> dict:
    """Sample RouterAgent output."""
    return {
        "department": "IT",
        "priority": "MEDIUM",
        "escalate_to_human": False,
        "escalation_reason": None,
        "suggested_sla_hours": 4,
        "routing_rules_applied": ["intent_to_department_mapping", "default_priority"]
    }


@pytest.fixture
def sample_action_result(mock_ticket_id: str) -> dict:
    """Sample ActionAgent output."""
    return {
        "ticket_id": mock_ticket_id,
        "ticket_url": f"https://servicenow.university.edu/ticket/{mock_ticket_id}",
        "department": "IT",
        "status": "created",
        "knowledge_articles": [
            {
                "article_id": "kb-001",
                "title": "How to Reset Your Canvas Password",
                "url": "https://kb.university.edu/canvas-password",
                "snippet": "Follow these steps to reset your Canvas password...",
                "relevance_score": 0.94,
                "department": "IT"
            }
        ],
        "estimated_response_time": "4 hours",
        "escalated": False,
        "user_message": "I've created a ticket for IT Support with medium priority. Expected response: within 4 hours."
    }


@pytest.fixture
def sample_knowledge_article() -> dict:
    """Sample knowledge base article."""
    return {
        "article_id": "kb-001",
        "title": "How to Reset Your Canvas Password",
        "url": "https://kb.university.edu/canvas-password",
        "snippet": "Follow these steps to reset your Canvas password...",
        "relevance_score": 0.94,
        "department": "IT"
    }


@pytest.fixture
def sample_session(mock_session_id: str, mock_student_id_hash: str) -> dict:
    """Sample session data."""
    now = datetime.now(timezone.utc).isoformat()
    return {
        "session_id": mock_session_id,
        "student_id_hash": mock_student_id_hash,
        "created_at": now,
        "last_active": now,
        "conversation_history": [],
        "clarification_attempts": 0,
        "ttl": 7776000  # 90 days
    }


@pytest.fixture
def mock_llm_service() -> MagicMock:
    """Mock LLM service for testing."""
    mock = MagicMock()
    mock.classify_intent = AsyncMock(return_value={
        "intent": "password_reset",
        "intent_category": "ACCOUNT_ACCESS",
        "confidence": 0.92,
        "entities": {},
        "sentiment": "NEUTRAL"
    })
    return mock


@pytest.fixture
def mock_ticket_service() -> MagicMock:
    """Mock ticketing service for testing."""
    mock = MagicMock()
    mock.create_ticket = AsyncMock(return_value={
        "ticket_id": "TKT-IT-20260120-0001",
        "status": "created"
    })
    mock.get_ticket_status = AsyncMock(return_value={
        "ticket_id": "TKT-IT-20260120-0001",
        "status": "open",
        "department": "IT"
    })
    return mock


@pytest.fixture
def mock_knowledge_service() -> MagicMock:
    """Mock knowledge base service for testing."""
    mock = MagicMock()
    mock.search = AsyncMock(return_value=[
        {
            "article_id": "kb-001",
            "title": "How to Reset Your Canvas Password",
            "url": "https://kb.university.edu/canvas-password",
            "relevance_score": 0.94
        }
    ])
    return mock


@pytest.fixture
def mock_session_store() -> MagicMock:
    """Mock session store for testing."""
    mock = MagicMock()
    mock.get_session = AsyncMock(return_value=None)
    mock.create_session = AsyncMock()
    mock.update_session = AsyncMock()
    return mock


# Environment variable fixtures
@pytest.fixture(autouse=True)
def set_test_env(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    """Set test environment variables.

    Skips overriding Azure OpenAI credentials for GPT-4o evaluation tests
    (test_gpt4o_evals.py) so they can use real API credentials.
    """
    # Check if this is a GPT-4o evaluation test that needs real credentials
    test_file = request.fspath.basename if request.fspath else ""
    if test_file == "test_gpt4o_evals.py":
        # Only set non-Azure-OpenAI env vars for eval tests
        monkeypatch.setenv("ENVIRONMENT", "test")
        # Don't set MOCK_MODE for eval tests - they need real API
        monkeypatch.setenv("COSMOS_DB_ENDPOINT", "https://test.documents.azure.com")
        monkeypatch.setenv("COSMOS_DB_KEY", "test-key")
        monkeypatch.setenv("SERVICENOW_INSTANCE", "test.service-now.com")
        monkeypatch.setenv("SERVICENOW_API_KEY", "test-key")
        monkeypatch.setenv("AZURE_SEARCH_ENDPOINT", "https://test.search.windows.net")
        monkeypatch.setenv("AZURE_SEARCH_API_KEY", "test-key")
        return

    # For all other tests, override with test credentials
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("MOCK_MODE", "true")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
    monkeypatch.setenv("COSMOS_DB_ENDPOINT", "https://test.documents.azure.com")
    monkeypatch.setenv("COSMOS_DB_KEY", "test-key")
    monkeypatch.setenv("SERVICENOW_INSTANCE", "test.service-now.com")
    monkeypatch.setenv("SERVICENOW_API_KEY", "test-key")
    monkeypatch.setenv("AZURE_SEARCH_ENDPOINT", "https://test.search.windows.net")
    monkeypatch.setenv("AZURE_SEARCH_API_KEY", "test-key")
