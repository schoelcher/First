import type { CalendarProvider } from "../providers/interfaces.js";
import type { CalendarEvent } from "../types.js";

export class GoogleCalendarProvider implements CalendarProvider {
  async listUpcomingEvents(_userId: string): Promise<CalendarEvent[]> {
    // TODO: Replace with Google Calendar API events.list + watch channel handling.
    return [
      {
        id: "evt-1",
        instanceId: "evt-1-2026-01-20",
        title: "Flight UA 100 to JFK",
        startAt: new Date(Date.now() + 6 * 60 * 60 * 1000).toISOString(),
        endAt: new Date(Date.now() + 8 * 60 * 60 * 1000).toISOString(),
        timezone: "America/Los_Angeles",
        location: "SFO",
        description: "Terminal 3",
      },
      {
        id: "evt-2",
        instanceId: "evt-2-2026-01-20",
        title: "Dinner with client",
        startAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
        endAt: new Date(Date.now() + 26 * 60 * 60 * 1000).toISOString(),
        timezone: "America/Los_Angeles",
        location: "The Progress, San Francisco",
      },
    ];
  }
}
