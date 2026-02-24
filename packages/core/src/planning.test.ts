import { describe, expect, it } from "vitest";
import { classifyFlightType, computeLeaveBy, requestWindow } from "./planning";

const settings = {
  meetingEarlyMins: 10,
  dinnerEarlyMins: 15,
  domesticFlightBufferMins: 90,
  internationalFlightBufferMins: 180,
  uncertaintyMaxMins: 20,
  uncertaintyPct: 0.1,
  uncertaintyBaseMins: 5,
  requestWindowStartMins: 30,
  requestWindowEndMins: 5,
  urgentThresholdMins: 45
};

describe("planning", () => {
  it("classifies international flights", () => {
    const type = classifyFlightType({
      eventTitle: "UA123 International departure",
      eventDescription: "passport required",
      etaMins: 40,
      eventStart: new Date("2026-01-01T12:00:00Z"),
      isAirport: true,
      settings
    });
    expect(type).toBe("international");
  });

  it("computes leave by", () => {
    const result = computeLeaveBy({
      eventTitle: "Team meeting",
      etaMins: 30,
      eventStart: new Date("2026-01-01T12:00:00Z"),
      isAirport: false,
      settings
    });
    expect(result.arriveBy.toISOString()).toBe("2026-01-01T11:50:00.000Z");
    expect(result.leaveBy.toISOString()).toBe("2026-01-01T11:12:00.000Z");
  });

  it("request window boundaries", () => {
    const leaveBy = new Date("2026-01-01T11:12:00Z");
    const open = requestWindow(new Date("2026-01-01T10:50:00Z"), leaveBy, settings);
    const closed = requestWindow(new Date("2026-01-01T10:30:00Z"), leaveBy, settings);
    expect(open.canRequestNow).toBe(true);
    expect(closed.canRequestNow).toBe(false);
  });
});
