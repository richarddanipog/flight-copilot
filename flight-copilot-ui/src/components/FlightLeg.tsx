import { memo, type FC, type JSX } from 'react';
import type { ILeg } from '../types/flight';

type FlightLegProps = {
  leg: ILeg;
};

const FlightLeg: FC<FlightLegProps> = ({ leg }) => {
  const fmtTime = (iso: string) => {
    const d = new Date(iso);
    const currentTime = d.toLocaleString([], {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });

    return currentTime.split(', ');
  };

  const fmtDur = (mins: number): string => {
    const h = Math.floor(mins / 60);
    const m = mins % 60;
    return `${h}h ${m}m`;
  };

  const stopsLabel = (n: number): string => {
    if (n === 0) return 'Direct';
    if (n === 1) return '1 stop';
    return `${n} stops`;
  };

  const convertDateTime = (iso: string): JSX.Element => {
    const [time, date] = fmtTime(iso);

    return (
      <div>
        <span className="w-20 font-semibold whitespace-nowrap tabular-nums">
          {date}
        </span>
        <br />
        <span className="w-20 text-xs whitespace-nowrap tabular-nums">
          {time}
        </span>
      </div>
    );
  };

  return (
    <div className="flex-1 flex flex-col justify-center mt-5">
      <div className="flex items-center gap-3">
        {convertDateTime(leg.depart_utc)}
        <div className="min-w-0">
          <div className="relative h-px bg-slate-200 w-full">
            <div className="absolute inset-y-0 left-0 right-0 h-px bg-slate-400" />
          </div>
          <div className="mt-1 text-xs text-blue-600">
            {stopsLabel(leg.stops)}
          </div>
        </div>
        {convertDateTime(leg.arrive_utc)}
      </div>

      <div className="mt-1 text-xs text-slate-500 whitespace-nowrap text-center">
        {leg.origin} → {leg.destination} • {fmtDur(leg.duration_min)}
      </div>
    </div>
  );
};

export default memo(FlightLeg);
