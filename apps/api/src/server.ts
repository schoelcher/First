import express from "express";
import helmet from "helmet";
import cors from "cors";
import cookieParser from "cookie-parser";
import rateLimit from "express-rate-limit";
import authRoutes from "./routes/auth";
import eventRoutes from "./routes/events";
import settingsRoutes from "./routes/settings";
import webhookRoutes from "./routes/webhooks";
import { env } from "./lib/env";

const app = express();
app.use(helmet());
app.use(cors({ origin: env.appUrl, credentials: true }));
app.use(express.json());
app.use(cookieParser());
app.use(rateLimit({ windowMs: 60_000, max: 100 }));

app.get("/health", (_req, res) => res.json({ ok: true }));
app.use("/auth", authRoutes);
app.use("/events", eventRoutes);
app.use("/settings", settingsRoutes);
app.use("/webhooks", webhookRoutes);

app.listen(env.port, () => {
  console.log(`API running on ${env.port}`);
});
