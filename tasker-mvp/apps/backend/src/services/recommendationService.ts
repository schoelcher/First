import type { RideProvider } from "../providers/interfaces.js";
import type { RideEstimate, RideRecommendation, TravelPlan } from "../types.js";

export class RecommendationService {
  constructor(private rideProvider: RideProvider) {}

  async recommend(plan: TravelPlan): Promise<RideRecommendation> {
    const estimates = await this.rideProvider.getEstimates(plan.origin, plan.destination);
    const feasible = estimates.filter((e) => e.tripDurationMinutes <= plan.etaMinutes + plan.variabilityMinutes + 15);
    const candidates = feasible.length ? feasible : estimates;
    const sorted = [...candidates].sort((a, b) => this.rank(a) - this.rank(b));
    return { plan, recommended: sorted[0], alternatives: sorted.slice(1) };
  }

  private rank(estimate: RideEstimate): number {
    return estimate.lowEstimate * 10 + (1 - (estimate.reliabilityScore ?? 0.8)) * 50;
  }
}
