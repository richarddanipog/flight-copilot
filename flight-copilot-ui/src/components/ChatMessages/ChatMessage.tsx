import { memo, useState, type FC } from 'react';
import type { IFlight } from '../../types/flight';
import { MarkdownTypewriter } from '../MarkdownTypewriter';
import FlightsList from '../FlightsList';

export type TChatMessage = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  data?: IFlight[];
};

const bubbleBase =
  'max-w-[85%] rounded-2xl px-4 py-2 text-sm shadow-sm break-words';

interface IChatMessageProps {
  message: TChatMessage;
  streamingMessageId?: string;
}

const ChatMessage: FC<IChatMessageProps> = ({
  message,
  streamingMessageId,
}) => {
  const [streamingComplete, onStreamingComplete] = useState(false);
  const isUser = message.role === 'user';
  const messageColor = isUser
    ? 'bg-blue-600 text-white rounded-br-sm'
    : 'bg-slate-100 text-slate-800 rounded-bl-sm';

  return (
    <div
      key={message.id}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div className={`${bubbleBase} ${messageColor}`}>
        {message.id === streamingMessageId ? (
          <>
            <MarkdownTypewriter
              content={message.content}
              speed={8}
              chunkSize={5}
              onComplete={() => onStreamingComplete(() => true)}
            />
            {streamingComplete && message.data && message.data.length > 0 && (
              <FlightsList flights={message.data} />
            )}
          </>
        ) : (
          <>
            <div className="whitespace-pre-wrap">{message.content}</div>
            {message.data && message.data.length > 0 && (
              <FlightsList flights={message.data} />
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default memo(ChatMessage);
