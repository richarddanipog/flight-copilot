import { api } from './client';
import mockData from '../mocks/agent-response.json';

const VITE_USE_MOCK = import.meta.env.VITE_USE_MOCK as boolean;

// If want to mock the /api/agent request in AI generate page.
const getMockData = () => mockData as any;

export const getAgentPromptResp = async <T>(body: unknown): Promise<T> => {
  if (VITE_USE_MOCK) getMockData();

  return api.post('/api/agent', body);
};
