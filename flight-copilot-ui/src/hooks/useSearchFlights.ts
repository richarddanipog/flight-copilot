import { useQuery } from '@tanstack/react-query';
import type { FlightSearchPayload } from '../types/flight';
import { postFlightSearch } from '../api/flights';

export const useSearchFlights = (payload: FlightSearchPayload | null) => {
  return useQuery({
    queryKey: ['searchFlight', payload],
    queryFn: () => postFlightSearch(payload!),
    enabled: !!payload,
    staleTime: 60 * 1000 * 3,
  });
};
