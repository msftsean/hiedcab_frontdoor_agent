/**
 * Header component with accessibility controls and navigation.
 */

import { SunIcon, MoonIcon, TrashIcon, ChatBubbleLeftRightIcon, TicketIcon, Cog6ToothIcon } from '@heroicons/react/24/outline';

type View = 'chat' | 'tickets' | 'admin';

interface HeaderProps {
  highContrast: boolean;
  onToggleHighContrast: () => void;
  onClearChat: () => void;
  onTalkToHuman: () => void;
  currentView: View;
  onViewChange: (view: View) => void;
}

export function Header({
  highContrast,
  onToggleHighContrast,
  onClearChat,
  onTalkToHuman,
  currentView,
  onViewChange,
}: HeaderProps) {
  return (
    <header
      className="bg-white border-b border-gray-200 shadow-sm"
      role="banner"
    >
      <div className="max-w-4xl mx-auto">
        {/* Top row: Logo and controls */}
        <div className="px-4 py-3 flex items-center justify-between">
          {/* Logo and title */}
          <div className="flex items-center gap-3">
            <div
              className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center"
              aria-hidden="true"
            >
              <svg
                className="w-6 h-6 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                />
              </svg>
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">
                University Support
              </h1>
              <p className="text-xs text-gray-500">
                Get help with IT, registration, financial aid, and more
              </p>
            </div>
          </div>

          {/* Controls */}
          <div className="flex items-center gap-2">
            {/* High contrast toggle */}
            <button
              onClick={onToggleHighContrast}
              className="p-2 rounded-lg hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
              aria-label={`${highContrast ? 'Disable' : 'Enable'} high contrast mode`}
              aria-pressed={highContrast}
            >
              {highContrast ? (
                <SunIcon className="w-5 h-5 text-gray-600" />
              ) : (
                <MoonIcon className="w-5 h-5 text-gray-600" />
              )}
            </button>

            {/* Clear chat button (only in chat view) */}
            {currentView === 'chat' && (
              <button
                onClick={onClearChat}
                className="p-2 rounded-lg hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
                aria-label="Clear chat history"
              >
                <TrashIcon className="w-5 h-5 text-gray-600" />
              </button>
            )}

            {/* Talk to human button */}
            <button
              onClick={onTalkToHuman}
              className="ml-2 px-4 py-2 text-sm font-medium text-primary-600 border border-primary-600 rounded-lg hover:bg-primary-50 focus:outline-none focus:ring-2 focus:ring-primary-500"
              aria-label="Request to speak with a human agent"
            >
              Talk to a Human
            </button>
          </div>
        </div>

        {/* Navigation tabs */}
        <nav className="px-4" aria-label="Main navigation">
          <div className="flex gap-1 border-t border-gray-100 -mb-px">
            <button
              onClick={() => onViewChange('chat')}
              className={`
                flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors
                focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500
                ${currentView === 'chat'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
              `}
              aria-current={currentView === 'chat' ? 'page' : undefined}
            >
              <ChatBubbleLeftRightIcon className="w-5 h-5" aria-hidden="true" />
              Chat
            </button>
            <button
              onClick={() => onViewChange('tickets')}
              className={`
                flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors
                focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500
                ${currentView === 'tickets'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
              `}
              aria-current={currentView === 'tickets' ? 'page' : undefined}
            >
              <TicketIcon className="w-5 h-5" aria-hidden="true" />
              My Tickets
            </button>
            <button
              onClick={() => onViewChange('admin')}
              className={`
                flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors
                focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500
                ${currentView === 'admin'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
              `}
              aria-current={currentView === 'admin' ? 'page' : undefined}
            >
              <Cog6ToothIcon className="w-5 h-5" aria-hidden="true" />
              Admin
            </button>
          </div>
        </nav>
      </div>
    </header>
  );
}
