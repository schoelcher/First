import { Router } from "express";
import { z } from "zod";
import type { RideProvider } from "../providers/interfaces.js";
import { logAction } from "../db/store.js";

export function ridesRouter(rideProvider: RideProvider) {
  const router = Router();

  router.post("/confirm", async (req, res) => {
    const schema = z.object({
      userId: z.string().default("demo-user"),
      approvedCharge: z.boolean(),
      productId: z.string(),
      origin: z.string(),
      destination: z.string(),
      latestArrivalIso: z.string(),
    });
    const payload = schema.parse(req.body ?? {});
    if (!payload.approvedCharge) return res.status(400).json({ error: "Explicit charge approval required" });

    const booked = await rideProvider.requestRide(payload);
    logAction(payload.userId, "ride_booked", booked);
    res.json(booked);
  });

  router.post("/cancel", (req, res) => {
    const { userId = "demo-user", rideId } = req.body ?? {};
    logAction(userId, "ride_cancelled", { rideId });
    res.json({ ok: true, rideId });
  });

  return router;
}
