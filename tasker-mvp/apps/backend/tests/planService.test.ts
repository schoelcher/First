import { describe, expect, it } from "vitest";
import { PlanService } from "../src/services/planService.js";
import type { RoutingProvider } from "../src/providers/interfaces.js";
import type { CalendarEvent, UserSettings } from "../src/types.js";

const routing: RoutingProvider = {
  estimateRoute: async () => ({ etaMinutes: 50, variabilityMinutes: 8 }),
};

const settings: UserSettings = {
  userId: "u1",
  homeBase: "1 Market St, San Francisco, CA",
  meetingEarlyMinutes: 10,
  dinnerEarlyMinutes: 15,
  domesticFlightMinutes: 90,
  internationalFlightMinutes: 180,
  cushionPercent: 0.1,
  cushionBaseMinutes: 5,
  cushionCapMinutes: 20,
  quietHoursStart: 22,
  quietHoursEnd: 7,
  urgencyThresholdMinutes: 45,
  notificationLeadMinutes: 20,
};

describe("PlanService", () => {
  it("applies dinner buffer", async () => {
    const svc = new PlanService(routing);
    const event: CalendarEvent = {
      id: "e1", instanceId: "e1", title: "Dinner", startAt: "2026-01-10T20:00:00.000Z", endAt: "2026-01-10T21:00:00.000Z", timezone: "UTC", location: "Some Restaurant",
    };
    const plan = await svc.computePlan({ event, settings, now: new Date("2026-01-10T15:00:00.000Z") });
    expect(plan?.eventKind).toBe("dinner");
    expect(plan?.flightMode).toBe("none");
  });

  it("classifies international flights via passport hint", async () => {
    const svc = new PlanService(routing);
    const event: CalendarEvent = {
      id: "e2", instanceId: "e2", title: "Flight AF84", description: "Passport check", startAt: "2026-01-10T20:00:00.000Z", endAt: "2026-01-10T21:00:00.000Z", timezone: "UTC", location: "SFO",
    };
    const plan = await svc.computePlan({ event, settings, now: new Date("2026-01-10T15:00:00.000Z") });
    expect(plan?.flightMode).toBe("international");
  });

  it("ignores virtual events", async () => {
    const svc = new PlanService(routing);
    const event: CalendarEvent = {
      id: "e3", instanceId: "e3", title: "Sync", startAt: "2026-01-10T20:00:00.000Z", endAt: "2026-01-10T21:00:00.000Z", timezone: "UTC", location: "Zoom meeting",
    };
    const plan = await svc.computePlan({ event, settings });
    expect(plan).toBeNull();
  });
});
