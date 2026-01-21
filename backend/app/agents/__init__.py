"""
Agent implementations for the Front Door Support Agent.
Three-agent architecture with bounded authority:
- QueryAgent: Intent detection and entity extraction
- RouterAgent: Routing decisions and escalation logic
- ActionAgent: Ticket creation and knowledge retrieval
"""

from app.agents.query_agent import QueryAgent
from app.agents.router_agent import RouterAgent
from app.agents.action_agent import ActionAgent

__all__ = ["QueryAgent", "RouterAgent", "ActionAgent"]
