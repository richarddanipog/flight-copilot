import { useEffect, useRef } from 'react';
import ChatMessage, { type TChatMessage } from './ChatMessage';

type Props = {
  messages: TChatMessage[];
  streamingMessageId?: string;
};

export default function ChatMessageList({
  messages,
  streamingMessageId,
}: Props) {
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    listRef.current?.scrollTo({
      top: listRef.current.scrollHeight,
      behavior: 'smooth',
    });
  }, [messages, streamingMessageId]);

  return (
    <div
      ref={listRef}
      className="overflow-y-auto space-y-5 pr-1"
      aria-live="polite"
    >
      {messages.map((m) => {
        return (
          <ChatMessage
            key={m.id}
            message={m}
            streamingMessageId={streamingMessageId}
          />
        );
      })}
    </div>
  );
}
