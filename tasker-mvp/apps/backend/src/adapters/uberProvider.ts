import type { RideProvider } from "../providers/interfaces.js";
import type { RideEstimate } from "../types.js";

export class UberRideProvider implements RideProvider {
  async getEstimates(_origin: string, destination: string): Promise<RideEstimate[]> {
    const airport = /\b[A-Z]{3}\b|airport/i.test(destination);
    return [
      { productId: "uberx", displayName: "UberX", lowEstimate: airport ? 38 : 14, highEstimate: airport ? 54 : 24, pickupEtaMinutes: 6, tripDurationMinutes: airport ? 52 : 34, reliabilityScore: 0.88 },
      { productId: "comfort", displayName: "Comfort", lowEstimate: airport ? 49 : 19, highEstimate: airport ? 72 : 31, pickupEtaMinutes: 7, tripDurationMinutes: airport ? 51 : 33, reliabilityScore: 0.9 },
      { productId: "xl", displayName: "UberXL", lowEstimate: airport ? 63 : 27, highEstimate: airport ? 85 : 43, pickupEtaMinutes: 8, tripDurationMinutes: airport ? 54 : 36, reliabilityScore: 0.83 },
    ];
  }

  async requestRide(input: { userId: string; productId: string; origin: string; destination: string; latestArrivalIso: string }): Promise<{ rideId: string; status: string }> {
    return { rideId: `ride_${input.productId}_${Date.now()}`, status: "processing" };
  }
}
