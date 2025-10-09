import { useQuery } from '@tanstack/react-query';
import { fetchAirports } from '../api/flights';

export const useAirports = (search: string) => {
  return useQuery({
    queryKey: ['airports', search],
    queryFn: () => fetchAirports(search),
    enabled: !!search && search.length > 1,
    staleTime: 60 * 1000 * 3,
  });
};
