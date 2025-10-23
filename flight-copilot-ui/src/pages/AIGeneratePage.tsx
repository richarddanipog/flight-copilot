import { useEffect, useRef, useState } from 'react';
import { useAIGeneratePrompt } from '../hooks/useAIGeneratePrompt';
import ChatMessageList from '../components/ChatMessages/ChatMessageList';
import type { TChatMessage } from '../components/ChatMessages/ChatMessage';

const EXAMPLES = [
  'find me a flight from tel aviv to prague in mid-november, under 500 usd',
  'tlv to bcn early december for a week non stop',
  'fine me a flights from tel aviv to prague in 2025-12-20 to 2025-12-30',
];

const AIGeneratePage = () => {
  const [chatHistory, setChatHistory] = useState<TChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [prompt, setPrompt] = useState('');
  const [streamingMessageId, setStreamingMessageId] = useState<
    string | undefined
  >(undefined);
  const awaitingRef = useRef(false); // avoids duplicate assistant appends per prompt
  const currentPromptRef = useRef<string>(''); // remember which prompt we're answering

  const { data: results, isLoading, error } = useAIGeneratePrompt(prompt);

  const makeId = () => `${Date.now()}-${Math.random().toString(16).slice(2)}`;

  const handleGenerate = async () => {
    const text = input.trim();
    if (!text) return;

    const userMsg: TChatMessage = { id: makeId(), role: 'user', content: text };
    setChatHistory((prev) => [...prev, userMsg]);

    currentPromptRef.current = text;
    awaitingRef.current = true;
    setPrompt(text);
    setInput('');
  };

  // When results for the current prompt arrive, append exactly one assistant message
  useEffect(() => {
    if (!results?.output) return;
    if (!awaitingRef.current) return; // already handled

    const assistantId = makeId();
    const assistantMsg: TChatMessage = {
      id: assistantId,
      role: 'assistant',
      content: String(results.output),
      data: results?.options,
    };
    setChatHistory((prev) => [...prev, assistantMsg]);
    setStreamingMessageId(assistantId);

    // guard so we don't append again on re-render
    awaitingRef.current = false;
  }, [results]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleGenerate();
    }
  };

  return (
    <div className="space-y-4">
      {/* <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-md break-words"> */}
      <div>
        {!chatHistory.length && (
          <>
            <h2 className="text-xl font-semibold text-slate-800 mb-3">
              AI trip planner
            </h2>
            <div className="flex flex-wrap gap-2 mb-3">
              {EXAMPLES.map((ex) => (
                <button
                  key={ex}
                  onClick={() => setInput(ex)}
                  className="rounded-full bg-slate-100 hover:bg-slate-200 px-3 py-1 text-xs text-slate-700 cursor-pointer"
                >
                  {ex}
                </button>
              ))}
            </div>
          </>
        )}

        <section id="chat" className="mb-3">
          <ChatMessageList
            messages={chatHistory}
            streamingMessageId={streamingMessageId}
          />
        </section>

        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          rows={3}
          className="w-full rounded-xl border border-slate-300 p-3 outline-none focus:ring-2 focus:ring-blue-500 mt-3"
          placeholder=""
          onKeyDown={handleKeyDown}
        />

        <div className="mt-1">
          <button
            onClick={handleGenerate}
            disabled={isLoading}
            className="rounded-xl bg-blue-600 text-white px-4 py-2 hover:bg-blue-700 disabled:opacity-60 cursor-pointer"
          >
            {isLoading ? 'Thinking…' : 'Submit'}
          </button>
        </div>

        {error && (
          <div className="mt-3 rounded-lg bg-red-50 text-red-700 text-sm p-3">
            {error.message}
          </div>
        )}
      </div>
    </div>
  );
};

export default AIGeneratePage;
