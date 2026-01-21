/**
 * Chat input component with accessibility support.
 */

import { useState, useRef, useCallback, KeyboardEvent } from 'react';
import { PaperAirplaneIcon } from '@heroicons/react/24/solid';

interface ChatInputProps {
  onSend: (content: string) => Promise<void>;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled = false }: ChatInputProps) {
  const [value, setValue] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = useCallback(async () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;

    setValue('');
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }

    await onSend(trimmed);
  }, [value, disabled, onSend]);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLTextAreaElement>) => {
      // Submit on Enter (without Shift)
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
      }
    },
    [handleSubmit]
  );

  const handleInput = useCallback(() => {
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        200
      )}px`;
    }
  }, []);

  return (
    <div className="relative">
      <label htmlFor="chat-input" className="sr-only">
        Type your message
      </label>

      <textarea
        ref={textareaRef}
        id="chat-input"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        onInput={handleInput}
        disabled={disabled}
        placeholder="Type your message here..."
        rows={1}
        className={`
          w-full resize-none rounded-xl border border-gray-300
          px-4 py-3 pr-12 text-sm
          placeholder:text-gray-400
          focus:border-primary-500 focus:ring-2 focus:ring-primary-500 focus:outline-none
          disabled:bg-gray-50 disabled:cursor-not-allowed
        `}
        aria-label="Message input"
        aria-describedby="input-instructions"
      />

      <p id="input-instructions" className="sr-only">
        Press Enter to send, Shift+Enter for a new line
      </p>

      <button
        onClick={handleSubmit}
        disabled={disabled || !value.trim()}
        className={`
          absolute right-2 top-1/2 -translate-y-1/2
          p-2 rounded-lg
          ${
            value.trim() && !disabled
              ? 'bg-primary-600 text-white hover:bg-primary-700'
              : 'bg-gray-100 text-gray-400 cursor-not-allowed'
          }
          focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
          transition-colors
        `}
        aria-label="Send message"
      >
        <PaperAirplaneIcon className="w-5 h-5" />
      </button>
    </div>
  );
}
