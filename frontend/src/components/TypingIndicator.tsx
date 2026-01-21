/**
 * Typing indicator component shown when assistant is responding.
 */

export function TypingIndicator() {
  return (
    <div
      className="flex justify-start"
      role="status"
      aria-label="Support agent is typing"
    >
      <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-md shadow-sm px-4 py-3">
        <div className="flex items-center gap-1">
          <span className="typing-dot w-2 h-2 bg-gray-400 rounded-full" />
          <span className="typing-dot w-2 h-2 bg-gray-400 rounded-full" />
          <span className="typing-dot w-2 h-2 bg-gray-400 rounded-full" />
        </div>
        <span className="sr-only">Support agent is typing a response</span>
      </div>
    </div>
  );
}
