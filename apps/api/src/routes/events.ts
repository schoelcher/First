import { Router } from "express";
import { z } from "zod";
import { PlannerService } from "../services/plannerService";
import { GoogleMapsProvider } from "../adapters/googleMapsProvider";
import { UberProvider } from "../adapters/uberProvider";
import { prisma } from "../lib/prisma";

const router = Router();
const planner = new PlannerService(new GoogleMapsProvider(), new UberProvider());

router.get("/:userId", async (req, res) => {
  const userId = req.params.userId;
  if (userId === "demo-user") {
    const existing = await prisma.user.findFirst({ where: { email: "demo@example.com" } });
    if (!existing) {
      await prisma.user.create({
        data: {
          email: "demo@example.com",
          homeBase: "1 Market St, San Francisco, CA",
          settingsJson: JSON.stringify({
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
          })
        }
      });
    }
    const demo = await prisma.user.findFirstOrThrow({ where: { email: "demo@example.com" } });
    await prisma.event.upsert({
      where: { userId_providerEventId: { userId: demo.id, providerEventId: "demo_evt_1" } },
      update: {},
      create: {
        userId: demo.id,
        providerEventId: "demo_evt_1",
        title: "Dinner reservation",
        startsAt: new Date(Date.now() + 90 * 60 * 1000),
        locationName: "SFO"
      }
    });
    const data = await planner.buildRecommendations(demo.id);
    return res.json(data);
  }
  const data = await planner.buildRecommendations(userId);
  res.json(data);
});

router.post("/:eventId/confirm", async (req, res) => {
  const body = z.object({ approveCharge: z.literal(true) }).parse(req.body);
  const uber = new UberProvider();
  const event = await prisma.event.findUniqueOrThrow({ where: { id: req.params.eventId } });
  const mode = uber.detectMode();
  const result = await uber.confirmBooking({ mode, approval: body.approveCharge, eventId: event.id });
  res.json({ mode, ...result });
});

router.post("/:eventId/not-traveling", async (req, res) => {
  await prisma.event.update({ where: { id: req.params.eventId }, data: { status: "not_traveling" } });
  res.status(204).send();
});

export default router;
