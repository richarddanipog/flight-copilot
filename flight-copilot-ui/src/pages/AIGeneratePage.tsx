import { useState } from 'react';
import { useAIGeneratePrompt } from '../hooks/useAIGeneratePrompt';
import FlightsList from '../components/FlightsList';
import { MarkdownTypewriter } from '../components/MarkdownTypewriter';

const EXAMPLES = [
  'find me a flight from tel aviv to prague in mid-november, under 500 usd, 4–6 days',
  'tlv to bcn early december for a week non stop',
  'rome next month weekend',
];

const AIGeneratePage = () => {
  const [input, setInput] = useState(EXAMPLES[0]);
  const [prompt, setPrompt] = useState('');
  const [showResults, setShowResults] = useState<boolean>(false);

  const { data: results, isLoading, error } = useAIGeneratePrompt(prompt);

  const handleGenerate = async () => {
    setPrompt(input);
  };

  return (
    <div className="space-y-4">
      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-md break-words">
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

        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          rows={3}
          className="w-full rounded-xl border border-slate-300 p-3 outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Describe your trip…"
        />

        <div className="mt-3">
          <button
            onClick={handleGenerate}
            disabled={isLoading}
            className="rounded-xl bg-blue-600 text-white px-4 py-2 hover:bg-blue-700 disabled:opacity-60 cursor-pointer"
          >
            {isLoading ? 'Thinking…' : 'Generate & Search'}
          </button>
        </div>

        {error && (
          <div className="mt-3 rounded-lg bg-red-50 text-red-700 text-sm p-3">
            {error.message}
          </div>
        )}

        {results?.output && (
          <div className="prose prose-sm max-w-none text-slate-700 mt-5 border-t-1 pt-2 border-slate-300">
            <MarkdownTypewriter
              content={results.output as string}
              speed={8}
              chunkSize={5}
              onComplete={() => setShowResults(true)}
            />
          </div>
        )}
      </div>

      {showResults && results && results.options.length > 0 && (
        <FlightsList flights={results.options} />
      )}
    </div>
  );
};

export default AIGeneratePage;
