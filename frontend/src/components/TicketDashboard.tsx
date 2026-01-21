/**
 * Ticket Dashboard component to display list of user's tickets.
 */

import {
  TicketIcon,
  ArrowPathIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';
import type { TicketSummary, TicketStatusResponse, Department, TicketStatus, Priority } from '../types';

const DEPARTMENT_LABELS: Record<Department, string> = {
  IT: 'IT Support',
  HR: 'Human Resources',
  REGISTRAR: "Registrar's Office",
  FINANCIAL_AID: 'Financial Aid',
  FACILITIES: 'Facilities',
  STUDENT_AFFAIRS: 'Student Affairs',
  CAMPUS_SAFETY: 'Campus Safety',
  ESCALATE_TO_HUMAN: 'Human Review',
};

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: typeof CheckCircleIcon }> = {
  open: { label: 'Open', color: 'bg-blue-100 text-blue-800', icon: TicketIcon },
  in_progress: { label: 'In Progress', color: 'bg-yellow-100 text-yellow-800', icon: ArrowPathIcon },
  pending_info: { label: 'Pending Info', color: 'bg-orange-100 text-orange-800', icon: ClockIcon },
  resolved: { label: 'Resolved', color: 'bg-green-100 text-green-800', icon: CheckCircleIcon },
  closed: { label: 'Closed', color: 'bg-gray-100 text-gray-800', icon: XMarkIcon },
  escalated: { label: 'Escalated', color: 'bg-purple-100 text-purple-800', icon: ExclamationCircleIcon },
};

const PRIORITY_CONFIG: Record<Priority, { label: string; color: string }> = {
  LOW: { label: 'Low', color: 'bg-gray-100 text-gray-700' },
  MEDIUM: { label: 'Medium', color: 'bg-blue-100 text-blue-700' },
  HIGH: { label: 'High', color: 'bg-orange-100 text-orange-700' },
  URGENT: { label: 'Urgent', color: 'bg-red-100 text-red-700' },
};

interface TicketDashboardProps {
  tickets: TicketSummary[];
  selectedTicket: TicketStatusResponse | null;
  isLoading: boolean;
  error: string | null;
  onRefresh: () => void;
  onSelectTicket: (ticketId: string) => void;
  onClearSelection: () => void;
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}

function TicketStatusBadge({ status }: { status: string }) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.open;
  const Icon = config.icon;

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${config.color}`}
    >
      <Icon className="w-3 h-3" aria-hidden="true" />
      {config.label}
    </span>
  );
}

function PriorityBadge({ priority }: { priority: Priority }) {
  const config = PRIORITY_CONFIG[priority];

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${config.color}`}
    >
      {config.label}
    </span>
  );
}

function TicketListItem({
  ticket,
  onClick,
}: {
  ticket: TicketSummary;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="w-full text-left p-4 hover:bg-gray-50 focus:outline-none focus:bg-gray-50 focus:ring-2 focus:ring-inset focus:ring-primary-500 border-b border-gray-200 last:border-b-0 transition-colors"
      aria-label={`View ticket ${ticket.ticket_id}`}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 mb-1">
            <code className="text-sm font-mono text-primary-600 font-medium">
              {ticket.ticket_id}
            </code>
            <TicketStatusBadge status={ticket.status} />
          </div>
          <p className="text-sm font-medium text-gray-900">{ticket.summary}</p>
          {ticket.description && (
            <p className="text-sm text-gray-600 mt-1 line-clamp-2">{ticket.description}</p>
          )}
          <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
            <span>{DEPARTMENT_LABELS[ticket.department] || ticket.department}</span>
            <span>|</span>
            <span>{formatDate(ticket.created_at)}</span>
          </div>
        </div>
        <svg
          className="w-5 h-5 text-gray-400 flex-shrink-0"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 5l7 7-7 7"
          />
        </svg>
      </div>
    </button>
  );
}

function TicketDetail({
  ticket,
  onClose,
}: {
  ticket: TicketStatusResponse;
  onClose: () => void;
}) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between">
          <div>
            <code className="text-lg font-mono text-primary-600 font-semibold">
              {ticket.ticket_id}
            </code>
            <div className="flex items-center gap-2 mt-1">
              <TicketStatusBadge status={ticket.status} />
              {ticket.priority && <PriorityBadge priority={ticket.priority} />}
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-primary-500"
            aria-label="Close ticket details"
          >
            <XMarkIcon className="w-5 h-5 text-gray-500" />
          </button>
        </div>
      </div>

      {/* Body */}
      <div className="p-4 space-y-4">
        {ticket.description && (
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
              Request
            </h4>
            <p className="text-sm text-gray-900 whitespace-pre-wrap">{ticket.description}</p>
          </div>
        )}

        <div>
          <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
            Department
          </h4>
          <p className="text-sm text-gray-900">
            {DEPARTMENT_LABELS[ticket.department] || ticket.department}
          </p>
        </div>

        <div>
          <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
            Created
          </h4>
          <p className="text-sm text-gray-900">{formatDate(ticket.created_at)}</p>
        </div>

        {ticket.updated_at && (
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
              Last Updated
            </h4>
            <p className="text-sm text-gray-900">{formatDate(ticket.updated_at)}</p>
          </div>
        )}

        {ticket.assigned_to && (
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
              Assigned To
            </h4>
            <p className="text-sm text-gray-900">{ticket.assigned_to}</p>
          </div>
        )}

        {ticket.resolution_summary && (
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
              Resolution
            </h4>
            <p className="text-sm text-gray-900">{ticket.resolution_summary}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export function TicketDashboard({
  tickets,
  selectedTicket,
  isLoading,
  error,
  onRefresh,
  onSelectTicket,
  onClearSelection,
}: TicketDashboardProps) {
  return (
    <div className="flex-1 flex flex-col p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">My Tickets</h2>
          <p className="text-sm text-gray-500">
            {tickets.length} ticket{tickets.length !== 1 ? 's' : ''}
          </p>
        </div>
        <button
          onClick={onRefresh}
          disabled={isLoading}
          className="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          aria-label="Refresh tickets"
        >
          <ArrowPathIcon
            className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`}
            aria-hidden="true"
          />
          Refresh
        </button>
      </div>

      {/* Error state */}
      {error && (
        <div
          className="mb-4 p-4 rounded-lg bg-red-50 border border-red-200 flex items-start gap-3"
          role="alert"
        >
          <ExclamationCircleIcon className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-red-800">Error</p>
            <p className="text-sm text-red-700">{error}</p>
          </div>
        </div>
      )}

      {/* Loading state */}
      {isLoading && tickets.length === 0 && (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <ArrowPathIcon className="w-8 h-8 text-gray-400 animate-spin mx-auto mb-2" />
            <p className="text-sm text-gray-500">Loading tickets...</p>
          </div>
        </div>
      )}

      {/* Empty state */}
      {!isLoading && tickets.length === 0 && !error && (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <TicketIcon className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <h3 className="text-sm font-medium text-gray-900 mb-1">No tickets yet</h3>
            <p className="text-sm text-gray-500">
              When you submit a support request, your tickets will appear here.
            </p>
          </div>
        </div>
      )}

      {/* Content */}
      {tickets.length > 0 && (
        <div className="flex-1 flex gap-4">
          {/* Ticket list */}
          <div
            className={`bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden ${
              selectedTicket ? 'w-1/2' : 'w-full'
            }`}
          >
            <div className="overflow-y-auto max-h-[calc(100vh-220px)]">
              {tickets.map((ticket) => (
                <TicketListItem
                  key={ticket.ticket_id}
                  ticket={ticket}
                  onClick={() => onSelectTicket(ticket.ticket_id)}
                />
              ))}
            </div>
          </div>

          {/* Ticket detail */}
          {selectedTicket && (
            <div className="w-1/2">
              <TicketDetail ticket={selectedTicket} onClose={onClearSelection} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
