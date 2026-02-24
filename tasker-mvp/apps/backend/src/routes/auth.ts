import { Router } from "express";

export const authRouter = Router();

authRouter.get("/google/start", (_req, res) => {
  // Replace with true OAuth flow.
  res.json({ url: "https://accounts.google.com/o/oauth2/v2/auth" });
});

authRouter.get("/google/callback", (_req, res) => {
  res.redirect(`${process.env.APP_BASE_URL}/events?connected=google`);
});

authRouter.get("/uber/start", (_req, res) => {
  res.json({ url: "https://auth.uber.com/oauth/v2/authorize" });
});
