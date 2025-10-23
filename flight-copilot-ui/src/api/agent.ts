import { api } from './client';
import mockData from '../mocks/travelpayouts.json';

const VITE_USE_MOCK = import.meta.env.VITE_USE_MOCK;

// If want to mock the /api/agent request in AI generate page.
const getMockData = () => mockData as any;

export const getAgentPromptResp = async <T>(body: unknown): Promise<T> => {
  if (VITE_USE_MOCK === 'true') return getMockData();

  return api.post('/api/agent', body);
};
