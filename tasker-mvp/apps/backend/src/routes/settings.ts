import { Router } from "express";
import { z } from "zod";
import { getSettings, saveSettings } from "../db/store.js";

export const settingsRouter = Router();

settingsRouter.get("/", (req, res) => {
  const userId = (req.query.userId as string) || "demo-user";
  res.json(getSettings(userId));
});

settingsRouter.put("/", (req, res) => {
  const body = z.object({ userId: z.string().default("demo-user") }).passthrough().parse(req.body ?? {});
  const updated = saveSettings(body.userId, body);
  res.json(updated);
});
