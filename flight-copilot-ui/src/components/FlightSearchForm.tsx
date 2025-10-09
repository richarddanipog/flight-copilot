import 'react-day-picker/dist/style.css';
import React, { useState } from 'react';
import type { AirportOption, FlightSearchPayload } from '../types/flight';
import { classNames, toISO } from '../utils';
import { AirportInput } from './AirportInput';
import { DateRangePicker } from './DateRangePicker';
import { useSearchFlights } from '../hooks/useSearchFlights';
import FlightsList from './FlightsList';

const FlightSearchForm = () => {
  const [from, setFrom] = useState<AirportOption | null>(null);
  const [to, setTo] = useState<AirportOption | null>(null);
  const [range, setRange] = useState<{ from?: Date; to?: Date }>({});
  const [nonStop, setNonStop] = useState(false);
  const [maxPrice, setMaxPrice] = useState<number | ''>('');
  const [payload, setPayload] = useState<FlightSearchPayload | null>(null);

  const { data, isLoading, error } = useSearchFlights(payload);

  const canSearch = from?.iata && to?.iata && range.from && range.to;

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSearch) return;

    const p: FlightSearchPayload = {
      origin: from!.iata,
      destination: to!.iata,
      departureDate: toISO(range.from!)!,
      returnDate: toISO(range.to!)!,
      maxPrice: maxPrice === '' ? undefined : Number(maxPrice),
      nonStop,
      currency: 'USD',
      max: 10,
    };

    setPayload(p);
  };

  return (
    <form
      onSubmit={onSubmit}
      className="max-w-7xl mx-auto px-4 py-8 bg-white rounded-2xl shadow-sm border border-slate-200 space-y-4"
    >
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <AirportInput label="From" value={from} onChange={setFrom} />
        <AirportInput label="To" value={to} onChange={setTo} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <DateRangePicker label="Dates" value={range} onChange={setRange} />
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Max Price (USD)
            </label>
            <input
              type="number"
              min={1}
              className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2 outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500"
              placeholder="e.g. 500"
              value={maxPrice}
              onChange={(e) =>
                setMaxPrice(e.target.value === '' ? '' : Number(e.target.value))
              }
            />
          </div>
          <div className="flex items-end">
            <label className="inline-flex items-center gap-2 select-none">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-slate-300"
                checked={nonStop}
                onChange={(e) => setNonStop(e.target.checked)}
              />
              <span className="text-sm text-slate-700">Non‑stop only</span>
            </label>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button
          type="submit"
          disabled={!canSearch || isLoading}
          className={classNames(
            'rounded-xl px-5 py-2.5 text-white',
            isLoading ? 'bg-blue-400' : 'bg-blue-600 hover:bg-blue-700',
            !canSearch ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer'
          )}
        >
          {isLoading ? 'Searching…' : 'Search Flights'}
        </button>
        {error && <div className="text-sm text-red-600">{error.message}</div>}
      </div>

      {data && data.options.length > 0 ? (
        <FlightsList flights={data.options} />
      ) : (
        data && (
          <div className="border-t-1 pt-3 border-slate-200">
            <span className="text-md text-gray-500">
              Flights not found in the date that you chosen please select
              different dates
            </span>
          </div>
        )
      )}
    </form>
  );
};

export default FlightSearchForm;
