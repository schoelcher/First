# Calendar → Uber Leave-By Assistant (MVP)

## Assumptions and decisions
- Booking mode is runtime-detected in `UberProvider.detectMode()`: `API_BOOKING` when `UBER_API_ENABLED=true`; otherwise `DEEPLINK_BOOKING` fallback. Both modes require explicit charge approval before action.
- Push notifications are modeled as preferred channel; email is mandatory fallback and SMS is optional (integration point in notification provider).
- Google Calendar integration is production-shaped (sync/watch token fields, webhook endpoint, resync path), while provider internals are stubbed for local MVP.
- Privacy-first storage: event IDs, normalized location, lat/lng, recommendation snapshots, and user settings only.

## High-level architecture

```text
┌───────────────┐      HTTPS       ┌────────────────────────────┐
│   Next.js PWA │ ───────────────▶ │ Express API (TypeScript)   │
│ mobile-first  │ ◀─────────────── │ Auth, Plans, Booking, CRUD │
└───────┬───────┘                  └────────────┬───────────────┘
        │                                        │
        │                                        │
        │                               ┌────────▼────────┐
        │                               │ Prisma + Postgres│
        │                               └────────┬────────┘
        │                                        │
        │                               ┌────────▼────────┐
        │                               │ BullMQ + Redis   │
        │                               └────────┬────────┘
        │                                        │
        │                         ┌──────────────┴───────────────────┐
        │                         │ Provider Adapters                 │
        │                         │ GoogleCalendar / Maps / Uber /   │
        └────────────────────────▶│ Notifications (push/email/SMS)   │
                                  └───────────────────────────────────┘
```

```text
Calendar Sync flow
Google Calendar watch webhook -> /webhooks/google/calendar
  -> CalendarProvider.syncEvents(incremental)
  -> if token invalid => full resync
  -> Planner recomputes leave_by + request windows
  -> Notification jobs scheduled
```

## Repo tree
```text
.
├── apps
│   ├── api
│   │   ├── prisma/schema.prisma
│   │   ├── src/adapters/*
│   │   ├── src/jobs/queue.ts
│   │   ├── src/lib/*
│   │   ├── src/routes/*
│   │   ├── src/services/plannerService.ts
│   │   └── src/server.ts
│   └── web
│       ├── app/*
│       ├── components/EventCard.tsx
│       └── public/manifest.json
├── packages/core/src/*
├── docker-compose.yml
└── .env.example
```

## Setup instructions
1. `npm install`
2. `docker compose up -d postgres redis`
3. Set `.env` from `.env.example`.
4. `npm run prisma:generate -w apps/api`
5. `npm run prisma:migrate -w apps/api -- --name init`
6. `npm run dev`

## Google Cloud setup
1. Create project, enable Calendar API.
2. Configure OAuth consent screen (external), add scopes `calendar.readonly`.
3. Create OAuth client (Web), redirect URI: `http://localhost:4000/auth/google/callback`.
4. Set webhook endpoint `http://localhost:4000/webhooks/google/calendar` and verify HTTPS in production.
5. Store client ID/secret in env.

## Uber setup
1. Create Uber developer app.
2. If Ride Request API scopes approved, set `UBER_API_ENABLED=true` and credentials.
3. If unavailable, keep false; app uses deep links (`m.uber.com`) after explicit approval.

## Maps setup
1. Enable Google Maps Directions + Geocoding APIs.
2. Add `GOOGLE_MAPS_API_KEY`.

## Web push + email + optional SMS
1. Generate VAPID keys, set env vars.
2. Configure SMTP creds (required fallback channel).
3. Optional: configure Twilio vars for urgent SMS route.

## Deploy recommendation (Render)
- Deploy `apps/api` as web service with managed Postgres + Redis.
- Deploy `apps/web` as static/web service pointing to API URL.
- Set same env vars in both services.
- Enable cron on API for channel renewal and sync backstop polling.

## Tests
- Unit tests for leave-by, flight classification, request windows: `packages/core/src/planning.test.ts`.
- Adapter integration stubs (mocked behavior): `apps/api/test/adapters.test.ts`.
