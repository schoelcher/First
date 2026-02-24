import { RoutingProvider } from "../lib/contracts";

export class GoogleMapsProvider implements RoutingProvider {
  async route(): Promise<{ etaMins: number; confidence: "low" | "medium" | "high" }> {
    return { etaMins: 28, confidence: "medium" };
  }

  async geocode(location: string): Promise<{ name: string; lat: number; lng: number; confidence: number }[]> {
    return [{ name: location, lat: 37.7749, lng: -122.4194, confidence: 0.9 }];
  }
}
