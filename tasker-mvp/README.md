# Tasker MVP (Google Calendar + Uber)

Mobile-first PWA + Node backend to compute leave-by times and request rides with explicit charge confirmation.

## Repo tree

```text
tasker-mvp/
  apps/
    backend/        # Express TypeScript API and planning logic
    web/            # Next.js App Router frontend (mobile-first)
  prisma/           # DB schema (Postgres)
  docs/             # Architecture + ops docs
  docker-compose.yml
  .env.example
```

## Core capabilities implemented
- Google Calendar provider abstraction with real adapter boundary.
- Away-location and virtual-event filtering heuristics.
- Leave-by algorithm with:
  - meeting/dinner early-arrival rules,
  - domestic vs international flight buffers,
  - uncertainty cushion formula.
- Recommendation engine choosing most affordable feasible ride.
- Explicit two-step approval before booking (`approvedCharge=true` required).
- Settings API for home base, buffers, cushion, quiet hours, notification lead time.
- Audit logs for recommendation/booking/cancellation.

## Local setup
1. Copy env values:
   ```bash
   cp .env.example .env
   ```
2. Run stack:
   ```bash
   docker compose up
   ```
3. Open web app: `http://localhost:3000`
4. API health: `http://localhost:4000/health`

## Provider setup guides

### Google Calendar
1. Create Google Cloud project.
2. Enable Google Calendar API.
3. Configure OAuth consent + scopes: `openid email profile https://www.googleapis.com/auth/calendar.readonly`.
4. Add redirect URI: `http://localhost:4000/auth/google/callback`.
5. Put credentials in `.env` (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`).
6. For push updates, configure watch channels endpoint and set `GOOGLE_WEBHOOK_URL`.

### Uber
1. Create Uber developer app.
2. Configure OAuth redirect URI `http://localhost:4000/auth/uber/callback`.
3. Set `UBER_CLIENT_ID`, `UBER_CLIENT_SECRET`.
4. Implement product/estimate/request calls in `UberRideProvider` for your account tier.

### Maps/Routing
1. Enable Google Maps Directions (or equivalent provider).
2. Set API key `MAPS_API_KEY`.
3. Replace stub implementation in `GoogleMapsProvider`.

## Recommended deployment
- Frontend: Vercel (Next.js).
- Backend: Fly.io/Render Node service.
- Data: managed Postgres + Redis.
- Set identical OAuth redirect URLs to deployed domains.

## Testing
```bash
npm run -w @tasker/backend test
```
