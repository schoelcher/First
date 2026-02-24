import { computeLeaveBy, requestWindow, UserSettings } from "@mvp/core";
import { RoutingProvider, RideProvider } from "../lib/contracts";
import { prisma } from "../lib/prisma";

const airportLookup: Record<string, string> = { SFO: "San Francisco International Airport", LAX: "Los Angeles International Airport", JFK: "John F Kennedy International Airport" };

export class PlannerService {
  constructor(private routing: RoutingProvider, private ride: RideProvider) {}

  async buildRecommendations(userId: string) {
    const user = await prisma.user.findUniqueOrThrow({ where: { id: userId } });
    const settings = JSON.parse(user.settingsJson) as UserSettings;
    const events = await prisma.event.findMany({ where: { userId, status: "active" }, orderBy: { startsAt: "asc" } });

    const enriched = [];
    for (const e of events) {
      if (!e.locationName || /(zoom|google meet|teams|webex|http|https)/i.test(e.locationName) || e.isVirtual) continue;
      const normalizedLocation = airportLookup[e.locationName.toUpperCase()] ?? e.locationName;
      const [geo] = await this.routing.geocode(normalizedLocation);
      const route = await this.routing.route(user.homeBase, geo.name, new Date());
      const plan = computeLeaveBy({ eventTitle: e.title, etaMins: route.etaMins, eventStart: e.startsAt, isAirport: /airport/i.test(normalizedLocation), settings });
      const pricing = await this.ride.estimateRide({ originLat: user.homeLat ?? 0, originLng: user.homeLng ?? 0, destLat: geo.lat, destLng: geo.lng });
      const window = requestWindow(new Date(), plan.leaveBy, settings);
      const recommendation = { pricing, route, window, bookingMode: this.ride.detectMode() };

      await prisma.event.update({
        where: { id: e.id },
        data: {
          locationLat: geo.lat,
          locationLng: geo.lng,
          leaveByAt: plan.leaveBy,
          arriveByAt: plan.arriveBy,
          recommendationJson: JSON.stringify(recommendation)
        }
      });

      enriched.push({ event: e, ...plan, recommendation });
    }
    return enriched;
  }
}
