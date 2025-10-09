import { useEffect, useMemo, useRef, useState } from 'react';
import { classNames, toISO } from '../utils';
import { DayPicker, type DateRange } from 'react-day-picker';

interface DateRangePickerProps {
  label: string;
  value: { from?: Date; to?: Date };
  onChange: (range: { from?: Date; to?: Date }) => void;
}

export const DateRangePicker = ({
  label,
  value,
  onChange,
}: DateRangePickerProps) => {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onDoc = (e: MouseEvent) => {
      if (!ref.current) return;
      if (!ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', onDoc);
    return () => document.removeEventListener('mousedown', onDoc);
  }, []);

  const text = useMemo(() => {
    const f = value.from ? toISO(value.from) : '';
    const t = value.to ? toISO(value.to) : '';
    return f && t ? `${f} → ${t}` : f || t || 'Pick dates';
  }, [value]);

  return (
    <div ref={ref} className="w-full">
      <label className="block text-sm font-medium text-slate-700 mb-1">
        {label}
      </label>
      <button
        type="button"
        className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2 text-left hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
        onClick={() => setOpen((v) => !v)}
      >
        <span
          className={classNames(
            'text-sm',
            text === 'Pick dates' && 'text-slate-500'
          )}
        >
          {text}
        </span>
      </button>
      {open && (
        <div className="relative z-10">
          <div className="absolute mt-2 rounded-xl border border-slate-200 bg-white p-2 shadow-xl">
            <DayPicker
              mode="range"
              numberOfMonths={2}
              selected={value as DateRange}
              onSelect={(r) => onChange(r ?? {})}
              disabled={{ before: new Date() }}
            />
          </div>
        </div>
      )}
    </div>
  );
};
