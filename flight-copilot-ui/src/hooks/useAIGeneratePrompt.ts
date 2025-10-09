import { useQuery } from '@tanstack/react-query';
import { getAgentPromptResp } from '../api/agent';
import type { ResponseFlightSearch } from '../types/flight';

export const useAIGeneratePrompt = (query: string) => {
  return useQuery({
    queryKey: ['generatePrompt', query],
    queryFn: () => getAgentPromptResp<ResponseFlightSearch>({ query }),
    enabled: !!query,
    staleTime: 60 * 1000 * 3,
  });
};
