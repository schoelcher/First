import type { RoutingProvider } from "../providers/interfaces.js";

export class GoogleMapsProvider implements RoutingProvider {
  async estimateRoute(_origin: string, destination: string, _arriveByIso: string): Promise<{ etaMinutes: number; variabilityMinutes: number }> {
    const airportish = /airport|\b[A-Z]{3}\b/.test(destination);
    return {
      etaMinutes: airportish ? 52 : 34,
      variabilityMinutes: airportish ? 9 : 6,
    };
  }
}
