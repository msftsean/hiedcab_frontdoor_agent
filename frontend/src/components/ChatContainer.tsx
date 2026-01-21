/**
 * Main chat container component.
 */

import { useRef, useEffect } from 'react';
import { MessageBubble } from './MessageBubble';
import { ChatInput } from './ChatInput';
import { TypingIndicator } from './TypingIndicator';
import type { Message } from '../types';

interface ChatContainerProps {
  messages: Message[];
  isLoading: boolean;
  sessionId: string | null;
  onSendMessage: (content: string) => Promise<void>;
}

export function ChatContainer({
  messages,
  isLoading,
  sessionId,
  onSendMessage,
}: ChatContainerProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatRegionRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Announce new messages to screen readers
  useEffect(() => {
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage.role === 'assistant') {
        // The aria-live region will announce this automatically
      }
    }
  }, [messages]);

  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-80px)]">
      {/* Messages area */}
      <div
        ref={chatRegionRef}
        className="flex-1 overflow-y-auto px-4 py-6 space-y-4"
        role="log"
        aria-label="Chat messages"
        aria-live="polite"
        aria-atomic="false"
      >
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}

        {isLoading && <TypingIndicator />}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="border-t border-gray-200 bg-white px-4 py-4">
        <ChatInput onSend={onSendMessage} disabled={isLoading} />

        {/* Session indicator */}
        {sessionId && (
          <p className="mt-2 text-xs text-gray-400 text-center">
            Session: {sessionId.slice(0, 8)}...
          </p>
        )}
      </div>
    </div>
  );
}
