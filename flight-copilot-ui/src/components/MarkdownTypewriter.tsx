import { useEffect, useMemo, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeSanitize from 'rehype-sanitize';

type Props = {
  content: string;
  speed?: number;
  chunkSize?: number;
  onComplete?: () => void;
  className?: string;
};

export const MarkdownTypewriter = ({
  content,
  speed = 8,
  chunkSize = 3,
  onComplete,
  className = '',
}: Props) => {
  const [visibleLength, setVisibleLength] = useState(0);

  // Normalize: collapse 3+ blank lines to two, trim edges.
  const normalized = useMemo(
    () => (content ?? '').replace(/\n{3,}/g, '\n\n').trim(),
    [content]
  );

  useEffect(() => {
    setVisibleLength(0);
  }, [normalized]);

  const contentLength = normalized.length;

  useEffect(() => {
    if (!contentLength || visibleLength >= contentLength) {
      return;
    }
    const t = setTimeout(
      () =>
        setVisibleLength((current) =>
          Math.min(current + chunkSize, contentLength)
        ),
      speed
    );
    return () => clearTimeout(t);
  }, [visibleLength, contentLength, chunkSize, speed]);

  useEffect(() => {
    if (!contentLength || visibleLength < contentLength) {
      return;
    }
    onComplete?.();
  }, [visibleLength, contentLength, onComplete]);

  useEffect(() => {
    if (visibleLength === 0 || typeof window === 'undefined') {
      return;
    }
    // Smooth scroll to bottom as content grows
    window.requestAnimationFrame(() => {
      window.scrollTo({
        top: document.documentElement.scrollHeight,
        behavior: 'smooth',
      });
    });
  }, [visibleLength]);

  const renderedContent = normalized.slice(0, visibleLength);

  return (
    <div className={`break-words ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeSanitize]}
        components={{
          p: ({ node, ...props }) => (
            <p className="my-3 leading-relaxed" {...props} />
          ),
          h4: ({ node, ...props }) => (
            <h4 className="mt-4 mb-2 font-semibold leading-snug" {...props} />
          ),
          strong: ({ node, ...props }) => (
            <strong className="font-semibold" {...props} />
          ),
        }}
      >
        {renderedContent}
      </ReactMarkdown>
    </div>
  );
};
