export type AirportOption = {
  iata: string;
  icao?: string;
  name: string;
  city?: string;
  country?: string;
  label?: string; // server returns label if you added it
};

export type FlightSearchPayload = {
  origin: string; // IATA
  destination: string; // IATA
  departureDate: string; // YYYY-MM-DD
  returnDate?: string; // YYYY-MM-DD
  maxPrice?: number;
  nonStop?: boolean;
  currency?: string;
  max?: number;
};

export type ResponseFlightSearch = {
  options: IFlight[];
  output?: string;
};

// The  interfaces of the response back from server
export interface IFlightPrice {
  amount: number;
  currency: string;
}

export interface ISegmentView {
  origin: string;
  destination: string;
  depart_utc: string;
  arrive_utc: string;
  carrier: string;
  flight_number?: string;
  duration_min: number;
}

export interface ILayoverView {
  at: string;
  duration_min: number;
}

export interface ILeg {
  origin: string;
  destination: string;
  depart_utc: string;
  arrive_utc: string;
  duration_min: number;
  stops: number;
  segments: ISegmentView[];
  layovers: ILayoverView[];
}

export interface IFlight {
  price: IFlightPrice;
  deeplink: null;
  carriers: string[];
  outbound: ILeg;
  return_: ILeg;
}
