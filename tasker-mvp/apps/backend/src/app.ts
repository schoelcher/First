import express from "express";
import { GoogleCalendarProvider } from "./adapters/googleCalendarProvider.js";
import { GoogleMapsProvider } from "./adapters/googleMapsProvider.js";
import { UberRideProvider } from "./adapters/uberProvider.js";
import { authRouter } from "./routes/auth.js";
import { eventsRouter } from "./routes/events.js";
import { ridesRouter } from "./routes/rides.js";
import { settingsRouter } from "./routes/settings.js";

export function createApp() {
  const app = express();
  app.use(express.json());

  const calendar = new GoogleCalendarProvider();
  const routing = new GoogleMapsProvider();
  const rides = new UberRideProvider();

  app.get("/health", (_req, res) => res.json({ ok: true }));
  app.use("/auth", authRouter);
  app.use("/settings", settingsRouter);
  app.use("/events", eventsRouter({ calendar, routing, rides }));
  app.use("/rides", ridesRouter(rides));

  return app;
}
