import type { CalendarEvent, TravelPlan, UserSettings } from "../types.js";
import type { RoutingProvider } from "../providers/interfaces.js";
import { classifyEventKind, classifyFlightMode, isVirtualEvent, normalizeDestination } from "./eventClassifier.js";

export class PlanService {
  constructor(private routingProvider: RoutingProvider) {}

  async computePlan(input: { event: CalendarEvent; previousEvent?: CalendarEvent; settings: UserSettings; now?: Date; flightOverride?: "domestic" | "international"; }): Promise<TravelPlan | null> {
    const { event, previousEvent, settings } = input;
    if (!event.location || isVirtualEvent(event)) return null;

    const destination = normalizeDestination(event.location);
    const origin = this.pickOrigin(previousEvent, settings.homeBase, event.startAt);
    const kind = classifyEventKind(event);
    const flightMode = kind === "flight" ? input.flightOverride ?? classifyFlightMode(event) : "none";

    const eventStart = new Date(event.startAt);
    const arriveBy = new Date(eventStart);
    arriveBy.setMinutes(arriveBy.getMinutes() - this.arrivalBuffer(kind, settings, flightMode));

    const route = await this.routingProvider.estimateRoute(origin, destination, arriveBy.toISOString());
    const cushion = Math.min(Math.round(route.etaMinutes * settings.cushionPercent) + settings.cushionBaseMinutes, settings.cushionCapMinutes);

    const leaveBy = new Date(arriveBy);
    leaveBy.setMinutes(leaveBy.getMinutes() - route.etaMinutes - cushion);

    const now = input.now ?? new Date();
    const minutesToLeave = Math.floor((leaveBy.getTime() - now.getTime()) / 60000);
    return {
      eventId: event.id,
      origin,
      destination,
      eventKind: kind,
      flightMode,
      etaMinutes: route.etaMinutes,
      variabilityMinutes: route.variabilityMinutes,
      arriveBy: arriveBy.toISOString(),
      leaveBy: leaveBy.toISOString(),
      confidence: route.variabilityMinutes <= 7 ? "high" : route.variabilityMinutes <= 12 ? "medium" : "low",
      urgent: minutesToLeave <= settings.urgencyThresholdMinutes,
    };
  }

  private pickOrigin(previousEvent: CalendarEvent | undefined, homeBase: string, nextStartIso: string): string {
    if (!previousEvent?.location) return homeBase;
    const gapMs = new Date(nextStartIso).getTime() - new Date(previousEvent.endAt).getTime();
    return gapMs <= 3 * 60 * 60 * 1000 && gapMs >= 0 ? normalizeDestination(previousEvent.location) : homeBase;
  }

  private arrivalBuffer(kind: string, settings: UserSettings, flightMode: "domestic" | "international" | "none"): number {
    if (kind === "flight") return flightMode === "international" ? settings.internationalFlightMinutes : settings.domesticFlightMinutes;
    if (kind === "dinner") return settings.dinnerEarlyMinutes;
    return settings.meetingEarlyMinutes;
  }
}
