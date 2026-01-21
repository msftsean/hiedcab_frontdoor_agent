/**
 * Type definitions for the Front Door Support Agent frontend.
 */

// =============================================================================
// Enums (matching backend)
// =============================================================================

export type Department =
  | 'IT'
  | 'HR'
  | 'REGISTRAR'
  | 'FINANCIAL_AID'
  | 'FACILITIES'
  | 'STUDENT_AFFAIRS'
  | 'CAMPUS_SAFETY'
  | 'ESCALATE_TO_HUMAN';

export type Priority = 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';

export type ActionStatus =
  | 'created'
  | 'escalated'
  | 'pending_clarification'
  | 'kb_only'
  | 'error';

export type EscalationReason =
  | 'confidence_too_low'
  | 'policy_keyword_detected'
  | 'sensitive_topic'
  | 'multi_department'
  | 'user_requested_human'
  | 'max_clarifications_exceeded';

export type TicketStatus =
  | 'open'
  | 'in_progress'
  | 'pending_info'
  | 'resolved'
  | 'closed';

// =============================================================================
// API Types
// =============================================================================

export interface ChatRequest {
  message: string;
  session_id: string | null;
}

export interface KnowledgeArticle {
  article_id: string;
  title: string;
  url: string;
  snippet?: string;
  relevance_score: number;
  department?: Department;
}

export interface ChatResponse {
  session_id: string;
  ticket_id: string | null;
  department: Department | null;
  status: ActionStatus;
  message: string;
  knowledge_articles: KnowledgeArticle[];
  escalated: boolean;
  escalation_reason: EscalationReason | null;
  estimated_response_time: string | null;
}

export interface TicketStatusResponse {
  ticket_id: string;
  department: Department;
  status: TicketStatus;
  priority?: Priority;
  summary?: string;
  description?: string;
  created_at: string;
  updated_at?: string;
  assigned_to?: string;
  resolution_summary?: string;
}

export interface TicketSummary {
  ticket_id: string;
  department: Department;
  status: string;
  created_at: string;
  summary: string;
  description?: string;
}

export interface TicketListResponse {
  tickets: TicketSummary[];
  total: number;
}

export interface KnowledgeSearchResponse {
  articles: KnowledgeArticle[];
  total_results: number;
}

export interface ServiceHealth {
  status: 'up' | 'down' | 'degraded';
  latency_ms?: number;
  error?: string;
}

export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  services: {
    llm: ServiceHealth;
    ticketing: ServiceHealth;
    knowledge_base: ServiceHealth;
    session_store: ServiceHealth;
  };
}

export interface ApiError {
  error: string;
  message: string;
  details?: Record<string, unknown>;
}

// =============================================================================
// UI Types
// =============================================================================

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  ticketId?: string;
  department?: Department;
  status?: ActionStatus;
  knowledgeArticles?: KnowledgeArticle[];
  escalated?: boolean;
  estimatedResponseTime?: string;
}

export interface ChatState {
  messages: Message[];
  isLoading: boolean;
  sessionId: string | null;
  error: string | null;
}

// =============================================================================
// Admin Types
// =============================================================================

export interface TicketUpdateRequest {
  status: TicketStatus;
  assigned_to?: string;
  resolution_summary?: string;
}
