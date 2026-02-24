import { Router } from "express";
import { prisma } from "../lib/prisma";

const router = Router();

router.post("/magic-link", async (req, res) => {
  const email = String(req.body.email ?? "").toLowerCase();
  const user = await prisma.user.upsert({
    where: { email },
    update: {},
    create: {
      email,
      homeBase: "San Francisco, CA",
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
  res.cookie("session", user.id, { httpOnly: true, secure: false, sameSite: "lax" });
  res.json({ userId: user.id });
});

router.post("/google/connect", async (_req, res) => {
  res.json({ authUrl: "https://accounts.google.com/o/oauth2/v2/auth?scope=calendar.readonly" });
});

export default router;
