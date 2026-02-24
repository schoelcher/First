export type EventKind = "meeting" | "dinner" | "flight" | "other";

export interface CalendarEvent {
  id: string;
  instanceId: string;
  title: string;
  description?: string;
  startAt: string;
  endAt: string;
  timezone: string;
  location?: string;
  conferenceData?: boolean;
}

export interface UserSettings {
  userId: string;
  homeBase: string;
  meetingEarlyMinutes: number;
  dinnerEarlyMinutes: number;
  domesticFlightMinutes: number;
  internationalFlightMinutes: number;
  cushionPercent: number;
  cushionBaseMinutes: number;
  cushionCapMinutes: number;
  quietHoursStart: number;
  quietHoursEnd: number;
  urgencyThresholdMinutes: number;
  notificationLeadMinutes: number;
}

export interface TravelPlan {
  eventId: string;
  origin: string;
  destination: string;
  eventKind: EventKind;
  flightMode: "domestic" | "international" | "none";
  etaMinutes: number;
  variabilityMinutes: number;
  arriveBy: string;
  leaveBy: string;
  confidence: "high" | "medium" | "low";
  urgent: boolean;
}

export interface RideEstimate {
  productId: string;
  displayName: string;
  lowEstimate: number;
  highEstimate: number;
  pickupEtaMinutes: number;
  tripDurationMinutes: number;
  reliabilityScore?: number;
}

export interface RideRecommendation {
  plan: TravelPlan;
  recommended: RideEstimate;
  alternatives: RideEstimate[];
}
