/**
 * Custom hook for managing chat state and interactions.
 */

import { useState, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { submitQuery, ApiClientError } from '../api/client';
import type { Message, ChatResponse } from '../types';

interface UseChatReturn {
  messages: Message[];
  isLoading: boolean;
  sessionId: string | null;
  error: string | null;
  sendMessage: (content: string) => Promise<void>;
  clearChat: () => void;
}

/**
 * Convert API response to a Message object.
 */
function responseToMessage(response: ChatResponse): Message {
  return {
    id: uuidv4(),
    role: 'assistant',
    content: response.message,
    timestamp: new Date(),
    ticketId: response.ticket_id ?? undefined,
    department: response.department ?? undefined,
    status: response.status,
    knowledgeArticles: response.knowledge_articles,
    escalated: response.escalated,
    estimatedResponseTime: response.estimated_response_time ?? undefined,
  };
}

/**
 * Custom hook for chat functionality.
 */
export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content:
        "Hello! I'm here to help you with university support requests. You can ask me about IT issues, registration, financial aid, facilities, and more. How can I help you today?",
      timestamp: new Date(),
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || isLoading) return;

      // Add user message
      const userMessage: Message = {
        id: uuidv4(),
        role: 'user',
        content: content.trim(),
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      setError(null);

      try {
        const response = await submitQuery(content.trim(), sessionId);

        // Update session ID
        if (response.session_id) {
          setSessionId(response.session_id);
        }

        // Add assistant response
        const assistantMessage = responseToMessage(response);
        setMessages((prev) => [...prev, assistantMessage]);
      } catch (err) {
        let errorMessage = 'An error occurred. Please try again.';

        if (err instanceof ApiClientError) {
          if (err.statusCode === 408) {
            errorMessage = 'Request timed out. Please try again.';
          } else if (err.statusCode === 429) {
            errorMessage = 'Too many requests. Please wait a moment and try again.';
          } else if (err.statusCode >= 500) {
            errorMessage = 'Service temporarily unavailable. Please try again later.';
          } else {
            errorMessage = err.message;
          }
        }

        setError(errorMessage);

        // Add error message to chat
        const errorResponseMessage: Message = {
          id: uuidv4(),
          role: 'assistant',
          content: errorMessage,
          timestamp: new Date(),
          status: 'error',
        };
        setMessages((prev) => [...prev, errorResponseMessage]);
      } finally {
        setIsLoading(false);
      }
    },
    [sessionId, isLoading]
  );

  const clearChat = useCallback(() => {
    setMessages([
      {
        id: 'welcome',
        role: 'assistant',
        content:
          "Hello! I'm here to help you with university support requests. You can ask me about IT issues, registration, financial aid, facilities, and more. How can I help you today?",
        timestamp: new Date(),
      },
    ]);
    setSessionId(null);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    sessionId,
    error,
    sendMessage,
    clearChat,
  };
}
