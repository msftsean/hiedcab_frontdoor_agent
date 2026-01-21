/**
 * Custom hook for managing ticket data and state.
 */

import { useState, useCallback, useEffect } from 'react';
import { listUserTickets, getTicketStatus, ApiClientError } from '../api/client';
import type { TicketSummary, TicketStatusResponse } from '../types';

interface UseTicketsReturn {
  tickets: TicketSummary[];
  selectedTicket: TicketStatusResponse | null;
  isLoading: boolean;
  error: string | null;
  refreshTickets: () => Promise<void>;
  selectTicket: (ticketId: string) => Promise<void>;
  clearSelection: () => void;
}

/**
 * Custom hook for ticket functionality.
 */
export function useTickets(): UseTicketsReturn {
  const [tickets, setTickets] = useState<TicketSummary[]>([]);
  const [selectedTicket, setSelectedTicket] = useState<TicketStatusResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshTickets = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await listUserTickets(undefined, 50);
      setTickets(response.tickets);
    } catch (err) {
      let errorMessage = 'Failed to load tickets. Please try again.';

      if (err instanceof ApiClientError) {
        if (err.statusCode === 401) {
          errorMessage = 'Please log in to view your tickets.';
        } else if (err.statusCode >= 500) {
          errorMessage = 'Service temporarily unavailable. Please try again later.';
        } else {
          errorMessage = err.message;
        }
      }

      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const selectTicket = useCallback(async (ticketId: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const ticket = await getTicketStatus(ticketId);
      setSelectedTicket(ticket);
    } catch (err) {
      let errorMessage = 'Failed to load ticket details. Please try again.';

      if (err instanceof ApiClientError) {
        if (err.statusCode === 404) {
          errorMessage = 'Ticket not found.';
        } else {
          errorMessage = err.message;
        }
      }

      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedTicket(null);
  }, []);

  // Load tickets on mount
  useEffect(() => {
    refreshTickets();
  }, [refreshTickets]);

  return {
    tickets,
    selectedTicket,
    isLoading,
    error,
    refreshTickets,
    selectTicket,
    clearSelection,
  };
}
