/**
 * Hook for admin ticket management.
 */

import { useState, useCallback, useEffect } from 'react';
import {
  adminListAllTickets,
  adminUpdateTicket,
  adminDeleteTicket,
  getTicketStatus,
} from '../api/client';
import type {
  TicketSummary,
  TicketStatusResponse,
  TicketStatus,
  Department,
} from '../types';

interface UseAdminTicketsResult {
  tickets: TicketSummary[];
  selectedTicket: TicketStatusResponse | null;
  isLoading: boolean;
  error: string | null;
  statusFilter: string | null;
  departmentFilter: Department | null;
  refreshTickets: () => Promise<void>;
  selectTicket: (ticketId: string) => Promise<void>;
  clearSelection: () => void;
  setStatusFilter: (status: string | null) => void;
  setDepartmentFilter: (department: Department | null) => void;
  updateTicketStatus: (
    ticketId: string,
    newStatus: TicketStatus,
    assignedTo?: string,
    resolutionSummary?: string
  ) => Promise<boolean>;
  deleteTicket: (ticketId: string) => Promise<boolean>;
}

export function useAdminTickets(): UseAdminTicketsResult {
  const [tickets, setTickets] = useState<TicketSummary[]>([]);
  const [selectedTicket, setSelectedTicket] = useState<TicketStatusResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [departmentFilter, setDepartmentFilter] = useState<Department | null>(null);

  const refreshTickets = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await adminListAllTickets(
        statusFilter || undefined,
        departmentFilter || undefined,
        50
      );
      setTickets(response.tickets);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load tickets';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [statusFilter, departmentFilter]);

  const selectTicket = useCallback(async (ticketId: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const ticket = await getTicketStatus(ticketId);
      setSelectedTicket(ticket);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load ticket details';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedTicket(null);
  }, []);

  const updateTicketStatus = useCallback(
    async (
      ticketId: string,
      newStatus: TicketStatus,
      assignedTo?: string,
      resolutionSummary?: string
    ): Promise<boolean> => {
      setIsLoading(true);
      setError(null);

      try {
        const updated = await adminUpdateTicket(ticketId, {
          status: newStatus,
          assigned_to: assignedTo,
          resolution_summary: resolutionSummary,
        });

        // Update selected ticket if it's the one being modified
        if (selectedTicket?.ticket_id === ticketId) {
          setSelectedTicket(updated);
        }

        // Refresh the list
        await refreshTickets();
        return true;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to update ticket';
        setError(message);
        return false;
      } finally {
        setIsLoading(false);
      }
    },
    [selectedTicket, refreshTickets]
  );

  const deleteTicket = useCallback(
    async (ticketId: string): Promise<boolean> => {
      setIsLoading(true);
      setError(null);

      try {
        await adminDeleteTicket(ticketId);

        // Clear selection if deleted ticket was selected
        if (selectedTicket?.ticket_id === ticketId) {
          setSelectedTicket(null);
        }

        // Refresh the list
        await refreshTickets();
        return true;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to delete ticket';
        setError(message);
        return false;
      } finally {
        setIsLoading(false);
      }
    },
    [selectedTicket, refreshTickets]
  );

  // Load tickets on mount and when filters change
  useEffect(() => {
    refreshTickets();
  }, [refreshTickets]);

  return {
    tickets,
    selectedTicket,
    isLoading,
    error,
    statusFilter,
    departmentFilter,
    refreshTickets,
    selectTicket,
    clearSelection,
    setStatusFilter,
    setDepartmentFilter,
    updateTicketStatus,
    deleteTicket,
  };
}
