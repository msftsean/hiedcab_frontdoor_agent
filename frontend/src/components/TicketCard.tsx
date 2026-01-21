/**
 * Ticket card component displayed when a ticket is created.
 */

import { ClipboardDocumentIcon, CheckIcon } from '@heroicons/react/24/outline';
import { useState, useCallback } from 'react';
import type { Department, ActionStatus } from '../types';

interface TicketCardProps {
  ticketId: string;
  department?: Department;
  status?: ActionStatus;
  estimatedResponseTime?: string;
  escalated?: boolean;
}

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

export function TicketCard({
  ticketId,
  department,
  status,
  estimatedResponseTime,
  escalated,
}: TicketCardProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(ticketId);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy ticket ID:', err);
    }
  }, [ticketId]);

  return (
    <div
      className={`
        rounded-lg p-3 text-sm
        ${escalated
          ? 'bg-warning-50 border border-warning-200'
          : 'bg-success-50 border border-success-200'
        }
      `}
      role="region"
      aria-label="Ticket information"
    >
      {/* Ticket ID with copy button */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="font-medium text-gray-900">Ticket:</span>
          <code className="bg-white px-2 py-0.5 rounded text-gray-800 font-mono text-xs">
            {ticketId}
          </code>
        </div>
        <button
          onClick={handleCopy}
          className="p-1 rounded hover:bg-white/50 focus:outline-none focus:ring-2 focus:ring-primary-500"
          aria-label={copied ? 'Copied!' : 'Copy ticket ID'}
        >
          {copied ? (
            <CheckIcon className="w-4 h-4 text-success-600" />
          ) : (
            <ClipboardDocumentIcon className="w-4 h-4 text-gray-500" />
          )}
        </button>
      </div>

      {/* Department */}
      {department && (
        <p className="mt-1 text-gray-600">
          <span className="font-medium">Department:</span>{' '}
          {DEPARTMENT_LABELS[department] || department}
        </p>
      )}

      {/* Response time */}
      {estimatedResponseTime && (
        <p className="mt-1 text-gray-600">
          <span className="font-medium">Expected response:</span>{' '}
          {estimatedResponseTime}
        </p>
      )}

      {/* Escalation notice */}
      {escalated && (
        <p className="mt-2 text-warning-700 font-medium">
          This request has been escalated to a human specialist.
        </p>
      )}
    </div>
  );
}
