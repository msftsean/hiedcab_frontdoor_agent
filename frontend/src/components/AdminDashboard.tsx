/**
 * Admin Dashboard component for ticket triage and management.
 */

import { useState } from 'react';
import {
  TicketIcon,
  ArrowPathIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  XMarkIcon,
  TrashIcon,
  PencilSquareIcon,
  FunnelIcon,
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

const DEPARTMENTS: Department[] = [
  'IT',
  'HR',
  'REGISTRAR',
  'FINANCIAL_AID',
  'FACILITIES',
  'STUDENT_AFFAIRS',
  'CAMPUS_SAFETY',
  'ESCALATE_TO_HUMAN',
];

const TICKET_STATUSES: TicketStatus[] = [
  'open',
  'in_progress',
  'pending_info',
  'resolved',
  'closed',
];

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

interface AdminDashboardProps {
  tickets: TicketSummary[];
  selectedTicket: TicketStatusResponse | null;
  isLoading: boolean;
  error: string | null;
  statusFilter: string | null;
  departmentFilter: Department | null;
  onRefresh: () => void;
  onSelectTicket: (ticketId: string) => void;
  onClearSelection: () => void;
  onSetStatusFilter: (status: string | null) => void;
  onSetDepartmentFilter: (department: Department | null) => void;
  onUpdateStatus: (
    ticketId: string,
    newStatus: TicketStatus,
    assignedTo?: string,
    resolutionSummary?: string
  ) => Promise<boolean>;
  onDeleteTicket: (ticketId: string) => Promise<boolean>;
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

function AdminTicketListItem({
  ticket,
  onClick,
  isSelected,
}: {
  ticket: TicketSummary;
  onClick: () => void;
  isSelected: boolean;
}) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left p-4 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500 border-b border-gray-200 last:border-b-0 transition-colors ${
        isSelected ? 'bg-primary-50' : 'hover:bg-gray-50'
      }`}
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
          <p className="text-sm font-medium text-gray-900 truncate">{ticket.summary}</p>
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

function AdminTicketDetail({
  ticket,
  onClose,
  onUpdateStatus,
  onDelete,
  isLoading,
}: {
  ticket: TicketStatusResponse;
  onClose: () => void;
  onUpdateStatus: (newStatus: TicketStatus, assignedTo?: string, resolutionSummary?: string) => Promise<boolean>;
  onDelete: () => Promise<boolean>;
  isLoading: boolean;
}) {
  const [isEditing, setIsEditing] = useState(false);
  const [newStatus, setNewStatus] = useState<TicketStatus>(ticket.status);
  const [assignedTo, setAssignedTo] = useState(ticket.assigned_to || '');
  const [resolutionSummary, setResolutionSummary] = useState(ticket.resolution_summary || '');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const handleSave = async () => {
    const success = await onUpdateStatus(
      newStatus,
      assignedTo || undefined,
      resolutionSummary || undefined
    );
    if (success) {
      setIsEditing(false);
    }
  };

  const handleDelete = async () => {
    await onDelete();
    setShowDeleteConfirm(false);
  };

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
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsEditing(!isEditing)}
              className="p-2 rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-primary-500"
              aria-label={isEditing ? 'Cancel editing' : 'Edit ticket'}
              disabled={isLoading}
            >
              <PencilSquareIcon className="w-5 h-5 text-gray-500" />
            </button>
            <button
              onClick={() => setShowDeleteConfirm(true)}
              className="p-2 rounded-lg hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-red-500"
              aria-label="Delete ticket"
              disabled={isLoading}
            >
              <TrashIcon className="w-5 h-5 text-red-500" />
            </button>
            <button
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-primary-500"
              aria-label="Close ticket details"
            >
              <XMarkIcon className="w-5 h-5 text-gray-500" />
            </button>
          </div>
        </div>
      </div>

      {/* Delete confirmation */}
      {showDeleteConfirm && (
        <div className="p-4 bg-red-50 border-b border-red-200">
          <p className="text-sm text-red-800 mb-3">
            Are you sure you want to delete this ticket? This action cannot be undone.
          </p>
          <div className="flex gap-2">
            <button
              onClick={handleDelete}
              disabled={isLoading}
              className="px-3 py-1.5 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50"
            >
              {isLoading ? 'Deleting...' : 'Delete'}
            </button>
            <button
              onClick={() => setShowDeleteConfirm(false)}
              disabled={isLoading}
              className="px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Body */}
      <div className="p-4 space-y-4">
        {/* Edit form */}
        {isEditing ? (
          <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
                Status
              </label>
              <select
                value={newStatus}
                onChange={(e) => setNewStatus(e.target.value as TicketStatus)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                {TICKET_STATUSES.map((status) => (
                  <option key={status} value={status}>
                    {STATUS_CONFIG[status]?.label || status}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
                Assigned To
              </label>
              <input
                type="text"
                value={assignedTo}
                onChange={(e) => setAssignedTo(e.target.value)}
                placeholder="Enter assignee name"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
                Resolution Summary
              </label>
              <textarea
                value={resolutionSummary}
                onChange={(e) => setResolutionSummary(e.target.value)}
                placeholder="Enter resolution notes"
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div className="flex gap-2">
              <button
                onClick={handleSave}
                disabled={isLoading}
                className="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 disabled:opacity-50"
              >
                {isLoading ? 'Saving...' : 'Save Changes'}
              </button>
              <button
                onClick={() => setIsEditing(false)}
                disabled={isLoading}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <>
            {ticket.summary && (
              <div>
                <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
                  Summary
                </h4>
                <p className="text-sm text-gray-900">{ticket.summary}</p>
              </div>
            )}

            {ticket.description && (
              <div>
                <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
                  Request Details
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
          </>
        )}
      </div>
    </div>
  );
}

export function AdminDashboard({
  tickets,
  selectedTicket,
  isLoading,
  error,
  statusFilter,
  departmentFilter,
  onRefresh,
  onSelectTicket,
  onClearSelection,
  onSetStatusFilter,
  onSetDepartmentFilter,
  onUpdateStatus,
  onDeleteTicket,
}: AdminDashboardProps) {
  const [showFilters, setShowFilters] = useState(false);

  return (
    <div className="flex-1 flex flex-col p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Admin Dashboard</h2>
          <p className="text-sm text-gray-500">
            {tickets.length} ticket{tickets.length !== 1 ? 's' : ''}
            {statusFilter && ` (${STATUS_CONFIG[statusFilter]?.label || statusFilter})`}
            {departmentFilter && ` in ${DEPARTMENT_LABELS[departmentFilter]}`}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`inline-flex items-center gap-2 px-3 py-2 text-sm font-medium border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 ${
              showFilters || statusFilter || departmentFilter
                ? 'text-primary-700 bg-primary-50 border-primary-300'
                : 'text-gray-700 bg-white border-gray-300 hover:bg-gray-50'
            }`}
          >
            <FunnelIcon className="w-4 h-4" />
            Filters
            {(statusFilter || departmentFilter) && (
              <span className="px-1.5 py-0.5 text-xs bg-primary-600 text-white rounded-full">
                {(statusFilter ? 1 : 0) + (departmentFilter ? 1 : 0)}
              </span>
            )}
          </button>
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
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="mb-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
          <div className="flex flex-wrap gap-4">
            <div className="flex-1 min-w-[200px]">
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
                Status
              </label>
              <select
                value={statusFilter || ''}
                onChange={(e) => onSetStatusFilter(e.target.value || null)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">All Statuses</option>
                {TICKET_STATUSES.map((status) => (
                  <option key={status} value={status}>
                    {STATUS_CONFIG[status]?.label || status}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex-1 min-w-[200px]">
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
                Department
              </label>
              <select
                value={departmentFilter || ''}
                onChange={(e) => onSetDepartmentFilter((e.target.value as Department) || null)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">All Departments</option>
                {DEPARTMENTS.map((dept) => (
                  <option key={dept} value={dept}>
                    {DEPARTMENT_LABELS[dept]}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex items-end">
              <button
                onClick={() => {
                  onSetStatusFilter(null);
                  onSetDepartmentFilter(null);
                }}
                className="px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </div>
      )}

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
            <h3 className="text-sm font-medium text-gray-900 mb-1">No tickets found</h3>
            <p className="text-sm text-gray-500">
              {statusFilter || departmentFilter
                ? 'Try adjusting your filters.'
                : 'When support requests are submitted, tickets will appear here.'}
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
            <div className="overflow-y-auto max-h-[calc(100vh-280px)]">
              {tickets.map((ticket) => (
                <AdminTicketListItem
                  key={ticket.ticket_id}
                  ticket={ticket}
                  onClick={() => onSelectTicket(ticket.ticket_id)}
                  isSelected={selectedTicket?.ticket_id === ticket.ticket_id}
                />
              ))}
            </div>
          </div>

          {/* Ticket detail */}
          {selectedTicket && (
            <div className="w-1/2">
              <AdminTicketDetail
                ticket={selectedTicket}
                onClose={onClearSelection}
                onUpdateStatus={(newStatus, assignedTo, resolutionSummary) =>
                  onUpdateStatus(selectedTicket.ticket_id, newStatus, assignedTo, resolutionSummary)
                }
                onDelete={() => onDeleteTicket(selectedTicket.ticket_id)}
                isLoading={isLoading}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
