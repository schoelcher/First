import { describe, expect, it } from "vitest";
import { RecommendationService } from "../src/services/recommendationService.js";
import type { RideProvider } from "../src/providers/interfaces.js";
import type { TravelPlan } from "../src/types.js";

const rides: RideProvider = {
  getEstimates: async () => [
    { productId: "x", displayName: "UberX", lowEstimate: 25, highEstimate: 35, pickupEtaMinutes: 5, tripDurationMinutes: 35, reliabilityScore: 0.9 },
    { productId: "comfort", displayName: "Comfort", lowEstimate: 30, highEstimate: 45, pickupEtaMinutes: 6, tripDurationMinutes: 35, reliabilityScore: 0.88 },
  ],
  requestRide: async () => ({ rideId: "r1", status: "processing" }),
};

describe("RecommendationService", () => {
  it("picks most affordable feasible product", async () => {
    const svc = new RecommendationService(rides);
    const plan: TravelPlan = {
      eventId: "e1", origin: "A", destination: "B", eventKind: "meeting", flightMode: "none",
      etaMinutes: 40, variabilityMinutes: 5, arriveBy: new Date().toISOString(), leaveBy: new Date().toISOString(), confidence: "high", urgent: false,
    };
    const rec = await svc.recommend(plan);
    expect(rec.recommended.productId).toBe("x");
  });
});
