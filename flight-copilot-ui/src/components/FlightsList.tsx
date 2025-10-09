import { memo } from 'react';
import FlightResultCard from './FlightResultCard';
import type { IFlight } from '../types/flight';

interface FlightsListProps {
  flights: IFlight[];
}

const FlightsList = memo(({ flights }: FlightsListProps) => {
  return (
    <div className="pt-2">
      <h3 className="text-lg font-semibold text-slate-800 mb-2">Results</h3>
      <ul className="space-y-2">
        {flights.map((r, idx) => (
          <li key={idx}>
            <FlightResultCard flight={r} />
          </li>
        ))}
      </ul>
    </div>
  );
});

export default FlightsList;
