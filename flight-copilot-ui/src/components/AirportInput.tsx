import { useEffect, useRef, useState } from 'react';
import { useDebouncedValue } from '../hooks/useDebounced';
import type { AirportOption } from '../types/flight';
import { classNames } from '../utils';
import { useAirports } from '../hooks/useAirports';

interface AirportInputProps {
  label: string;
  placeholder?: string;
  value?: AirportOption | null;
  onChange: (opt: AirportOption | null) => void;
}

export const AirportInput = ({
  label,
  placeholder,
  value,
  onChange,
}: AirportInputProps) => {
  const boxRef = useRef<HTMLDivElement>(null);
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState('');
  const debounced = useDebouncedValue(input);
  const { data, isLoading, error } = useAirports(debounced);

  useEffect(() => {
    const onDocClick = (e: MouseEvent) => {
      if (!boxRef.current) return;
      if (!boxRef.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', onDocClick);
    return () => document.removeEventListener('mousedown', onDocClick);
  }, []);

  return (
    <div ref={boxRef} className="w-full">
      <label className="block text-sm font-medium text-slate-700 mb-1">
        {label}
      </label>
      <div className="relative">
        <input
          className={classNames(
            'w-full rounded-xl border border-slate-300 bg-white px-4 py-2 outline-none',
            'focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500'
          )}
          placeholder={placeholder || 'Type city, airport or IATA'}
          value={open ? input : value?.label || ''}
          onChange={(e) => {
            setInput(e.target.value);
            setOpen(true);
          }}
          onFocus={() => setOpen(true)}
        />
        {open && (
          <div className="absolute z-20 mt-1 w-full rounded-xl border border-slate-200 bg-white shadow-lg max-h-72 overflow-auto">
            {isLoading && (
              <div className="px-4 py-3 text-sm text-slate-500">Loading…</div>
            )}
            {error && (
              <div className="px-4 py-3 text-sm text-red-600">
                {error.message}
              </div>
            )}
            {!isLoading && !error && data?.length === 0 && (
              <div className="px-4 py-3 text-sm text-slate-500">No results</div>
            )}
            {data?.map((opt) => (
              <button
                key={`${opt.iata}-${opt.name}`}
                type="button"
                className="flex w-full items-start gap-2 px-4 py-2 text-left hover:bg-slate-50"
                onClick={() => {
                  onChange(opt);
                  setOpen(false);
                }}
              >
                <div className="text-slate-900 text-sm font-medium">
                  {opt.label || `${opt.city ?? ''} — ${opt.name} (${opt.iata})`}
                </div>
                <div className="ml-auto text-xs text-slate-500">
                  {opt.country}
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
