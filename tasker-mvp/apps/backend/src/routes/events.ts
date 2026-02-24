import { Router } from "express";
import { z } from "zod";
import type { CalendarProvider, RideProvider, RoutingProvider } from "../providers/interfaces.js";
import { getSettings, logAction } from "../db/store.js";
import { PlanService } from "../services/planService.js";
import { RecommendationService } from "../services/recommendationService.js";

export function eventsRouter(deps: { calendar: CalendarProvider; routing: RoutingProvider; rides: RideProvider }) {
  const router = Router();
  const planService = new PlanService(deps.routing);
  const recService = new RecommendationService(deps.rides);

  router.get("/eligible", async (req, res) => {
    const userId = (req.query.userId as string) || "demo-user";
    const events = await deps.calendar.listUpcomingEvents(userId);
    const settings = getSettings(userId);

    const plans = await Promise.all(events.map((event, idx) => planService.computePlan({ event, previousEvent: events[idx - 1], settings })));
    res.json(plans.filter(Boolean));
  });

  router.post("/:eventId/recommendation", async (req, res) => {
    const schema = z.object({ userId: z.string().default("demo-user"), flightOverride: z.enum(["domestic", "international"]).optional() });
    const { userId, flightOverride } = schema.parse(req.body ?? {});
    const settings = getSettings(userId);
    const events = await deps.calendar.listUpcomingEvents(userId);
    const event = events.find((e) => e.id === req.params.eventId);
    if (!event) return res.status(404).json({ error: "Event not found" });

    const previousEvent = events[events.indexOf(event) - 1];
    const plan = await planService.computePlan({ event, previousEvent, settings, flightOverride });
    if (!plan) return res.status(422).json({ error: "Event is virtual or missing location" });

    const recommendation = await recService.recommend(plan);
    logAction(userId, "recommendation_created", recommendation);
    return res.json(recommendation);
  });

  return router;
}
