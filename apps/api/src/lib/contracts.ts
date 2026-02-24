export interface CalendarProvider {
  syncEvents(userId: string, fullResync?: boolean): Promise<void>;
  watchCalendar(userId: string): Promise<void>;
}

export interface RoutingProvider {
  route(origin: string, destination: string, departureTime: Date): Promise<{ etaMins: number; confidence: "low" | "medium" | "high" }>;
  geocode(location: string): Promise<{ name: string; lat: number; lng: number; confidence: number }[]>;
}

export interface RideProvider {
  detectMode(): "API_BOOKING" | "DEEPLINK_BOOKING";
  estimateRide(input: { originLat: number; originLng: number; destLat: number; destLng: number }): Promise<{ product: string; min: number; max: number; pickupEtaMins: number }>;
  confirmBooking(input: { mode: "API_BOOKING" | "DEEPLINK_BOOKING"; approval: boolean; eventId: string }): Promise<{ status: string; deeplink?: string; requestId?: string }>;
}

export interface NotificationProvider {
  sendLeaveReminder(input: { userId: string; eventId: string; urgent: boolean; title: string; body: string }): Promise<void>;
}
