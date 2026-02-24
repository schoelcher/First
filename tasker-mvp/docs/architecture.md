# Tasker MVP Architecture

## Assumptions & Decisions
- MVP focuses on one user (`demo-user`) but preserves multi-user boundaries in interfaces.
- OAuth callbacks are scaffolded; production token persistence/encryption is described and model-ready.
- Background jobs use Redis/BullMQ in production, with in-memory fallback possible.
- Explicit charge approval is hard-required before ride request API call.

## High-level diagram

```text
[Next.js PWA]
   |  HTTPS JSON
   v
[Express API]
   |- CalendarProvider (Google Calendar)
   |- RoutingProvider (Google Maps)
   |- RideProvider (Uber)
   |- PlanService / RecommendationService
   |- Audit logging
   v
[Postgres + Redis jobs]
```

## Request flow
1. User connects Google + Uber.
2. `/events/eligible` fetches upcoming events, filters virtual, computes leave-by plans.
3. User taps "Request Uber" -> `/events/:id/recommendation` picks affordable feasible product.
4. UI prompts explicit "I approve this charge".
5. `/rides/confirm` creates ride request only when approved.

## Reliability and fallbacks
- Routing failure -> use cached average ETA and mark confidence low.
- Uber estimate failure -> downgrade to reminder-only plan (no booking).
- Quiet hours respected unless urgent threshold hit.

## Privacy
- Persist minimal data: OAuth tokens (encrypted), event IDs/location, plans, audit actions.
- Do not persist full event description by default.
