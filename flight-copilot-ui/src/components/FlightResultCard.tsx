import type { FC } from 'react';
import { Heart, ChevronRight } from 'lucide-react';
import FlightLeg from './FlightLeg';
import type { IFlight } from '../types/flight';

type FlightResultCardProps = {
  flight: IFlight;
};

const FlightResultCard: FC<FlightResultCardProps> = ({ flight }) => {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white shadow-sm p-3 md:p-4">
      <div className="flex items-center gap-3">
        <div className="flex-3 flex items-center gap-3 h-full">
          <div className="h-[100px] sm:flex justify-center w-24 rounded-xl bg-slate-100 text-slate-600 font-semibold">
            <div className="text-md flex justify-center items-center">
              {flight.carriers[0]}
              {flight.carriers.length > 1 && (
                <div className="text-sm text-slate-500">
                  +{flight.carriers.length - 1}
                </div>
              )}
            </div>
          </div>

          <div className="flex-1">
            <FlightLeg leg={flight.outbound} />
            <FlightLeg leg={flight.return_} />
          </div>
        </div>

        <div className="hidden md:block col-span-1 h-24 border-l border-slate-200" />

        <div className="flex-1 ml-auto flex items-center justify-between md:justify-end gap-3">
          <div className="text-right">
            <div className="text-slate-900 font-bold text-lg whitespace-nowrap">
              {flight.price.amount}{' '}
              <span className="text-slate-500 text-sm">
                {flight.price.currency}
              </span>
            </div>
            <div className="text-xs text-slate-500">total price</div>
          </div>

          <a
            href={flight.deeplink || '#'}
            target="_blank"
            className="inline-flex items-center gap-1.5 rounded-xl bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
          >
            Select <ChevronRight className="h-4 w-4" />
          </a>

          <button
            className="rounded-full border border-slate-300 p-2 hover:bg-slate-50"
            aria-label="Save"
          >
            <Heart className="h-5 w-5 text-slate-600" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default FlightResultCard;
