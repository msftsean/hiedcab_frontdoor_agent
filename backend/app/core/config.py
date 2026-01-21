"""
Application configuration using Pydantic Settings.
Supports both environment variables and .env files.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ==========================================================================
    # Application Settings
    # ==========================================================================
    app_name: str = Field(default="Front Door Support Agent")
    app_version: str = Field(default="1.0.0")
    environment: Literal["development", "staging", "production", "test"] = Field(
        default="development"
    )
    debug: bool = Field(default=False)
    mock_mode: bool = Field(
        default=True,
        description="Use mock implementations for external services"
    )

    # ==========================================================================
    # API Settings
    # ==========================================================================
    api_prefix: str = Field(default="/api")
    allowed_origins: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"]
    )

    # ==========================================================================
    # Azure OpenAI Settings
    # ==========================================================================
    azure_openai_endpoint: str = Field(
        default="",
        description="Azure OpenAI endpoint URL"
    )
    azure_openai_api_key: str = Field(
        default="",
        description="Azure OpenAI API key"
    )
    azure_openai_deployment: str = Field(
        default="gpt-4o",
        description="Azure OpenAI deployment name"
    )
    azure_openai_api_version: str = Field(
        default="2024-02-15-preview",
        description="Azure OpenAI API version"
    )

    # ==========================================================================
    # Azure Cosmos DB Settings
    # ==========================================================================
    cosmos_db_endpoint: str = Field(
        default="",
        description="Azure Cosmos DB endpoint URL"
    )
    cosmos_db_key: str = Field(
        default="",
        description="Azure Cosmos DB primary key"
    )
    cosmos_db_database: str = Field(
        default="frontdoor",
        description="Cosmos DB database name"
    )
    cosmos_db_sessions_container: str = Field(
        default="sessions",
        description="Container for session data"
    )
    cosmos_db_audit_container: str = Field(
        default="audit_logs",
        description="Container for audit logs"
    )

    # ==========================================================================
    # Azure AI Search Settings
    # ==========================================================================
    azure_search_endpoint: str = Field(
        default="",
        description="Azure AI Search endpoint URL"
    )
    azure_search_api_key: str = Field(
        default="",
        description="Azure AI Search API key"
    )
    azure_search_index: str = Field(
        default="knowledge-base",
        description="Search index name"
    )

    # ==========================================================================
    # ServiceNow Settings
    # ==========================================================================
    servicenow_instance: str = Field(
        default="",
        description="ServiceNow instance URL (e.g., 'university.service-now.com')"
    )
    servicenow_api_key: str = Field(
        default="",
        description="ServiceNow API key"
    )
    servicenow_username: str = Field(
        default="",
        description="ServiceNow username (for basic auth if needed)"
    )
    servicenow_password: str = Field(
        default="",
        description="ServiceNow password (for basic auth if needed)"
    )

    # ==========================================================================
    # Session Settings
    # ==========================================================================
    session_ttl_seconds: int = Field(
        default=7776000,  # 90 days
        description="Session time-to-live in seconds"
    )
    max_clarification_attempts: int = Field(
        default=3,
        description="Maximum clarification attempts before escalation"
    )
    max_conversation_turns: int = Field(
        default=50,
        description="Maximum conversation turns to keep in history"
    )

    # ==========================================================================
    # Confidence Thresholds
    # ==========================================================================
    confidence_threshold: float = Field(
        default=0.70,
        ge=0.0,
        le=1.0,
        description="Minimum confidence for routing without clarification"
    )
    kb_relevance_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum relevance score for KB articles"
    )

    # ==========================================================================
    # Rate Limiting
    # ==========================================================================
    rate_limit_requests: int = Field(
        default=100,
        description="Maximum requests per window"
    )
    rate_limit_window_seconds: int = Field(
        default=60,
        description="Rate limit window in seconds"
    )

    # ==========================================================================
    # SLA Configuration (hours)
    # ==========================================================================
    sla_urgent_hours: int = Field(default=1)
    sla_high_hours: int = Field(default=4)
    sla_medium_hours: int = Field(default=24)
    sla_low_hours: int = Field(default=72)

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    @property
    def is_test(self) -> bool:
        """Check if running in test environment."""
        return self.environment == "test"

    @property
    def use_mock_services(self) -> bool:
        """Determine if mock services should be used."""
        return self.mock_mode or self.is_test


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
