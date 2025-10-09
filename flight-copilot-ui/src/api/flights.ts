import type {
  AirportOption,
  FlightSearchPayload,
  ResponseFlightSearch,
} from '../types/flight';
import { api } from './client';

export const fetchAirports = async (
  query: string
): Promise<AirportOption[]> => {
  return api.get('/api/locations', query);
};

export const postFlightSearch = async (
  payload: FlightSearchPayload
): Promise<ResponseFlightSearch> => {
  return api.post('/api/flights', payload);
};
