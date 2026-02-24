import type { CalendarEvent, RideEstimate } from "../types.js";

export interface CalendarProvider {
  listUpcomingEvents(userId: string): Promise<CalendarEvent[]>;
}

export interface RoutingProvider {
  estimateRoute(origin: string, destination: string, arriveByIso: string): Promise<{ etaMinutes: number; variabilityMinutes: number }>;
}

export interface RideProvider {
  getEstimates(origin: string, destination: string): Promise<RideEstimate[]>;
  requestRide(input: { userId: string; productId: string; origin: string; destination: string; latestArrivalIso: string }): Promise<{ rideId: string; status: string }>;
}
