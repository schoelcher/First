import { Router } from "express";
import { GoogleCalendarProvider } from "../adapters/googleCalendarProvider";

const router = Router();
const calendar = new GoogleCalendarProvider();

router.post("/google/calendar", async (req, res) => {
  const userId = String(req.headers["x-user-id"] ?? "");
  if (userId) await calendar.syncEvents(userId);
  res.status(202).send();
});

export default router;
