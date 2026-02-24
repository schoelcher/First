export type BookingMode = "API_BOOKING" | "DEEPLINK_BOOKING";

export interface UserSettings {
  meetingEarlyMins: number;
  dinnerEarlyMins: number;
  domesticFlightBufferMins: number;
  internationalFlightBufferMins: number;
  uncertaintyMaxMins: number;
  uncertaintyPct: number;
  uncertaintyBaseMins: number;
  requestWindowStartMins: number;
  requestWindowEndMins: number;
  urgentThresholdMins: number;
}

export interface LeaveByInput {
  eventTitle: string;
  eventDescription?: string;
  etaMins: number;
  eventStart: Date;
  isAirport: boolean;
  userFlightOverride?: "domestic" | "international";
  settings: UserSettings;
}
