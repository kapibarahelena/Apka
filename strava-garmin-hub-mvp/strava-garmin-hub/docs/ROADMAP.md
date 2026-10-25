# Roadmap and acceptance gates

## Slice 1 — foundations (this repository)
- [x] FastAPI app and health endpoint
- [x] PostgreSQL schema for activities, metrics, integrations, workouts and encrypted credentials
- [x] Strava OAuth state + encrypted credential storage and paginated activity import path
- [x] Basic dashboard/list/metrics/load/status/plan endpoints
- [x] Home Assistant config flow and sensor entities
- [x] Native Android Compose shell
- [x] Documentation and starter tests

## Slice 2 — reliable sync
- [ ] Alembic migrations
- [ ] Durable job queue/checkpoint model and idempotent resume
- [ ] Retry-After + backoff and rate-limit telemetry
- [ ] Strava detailed activity and streams ingestion
- [ ] Webhook subscription and periodic reconciliation
- [ ] Test OAuth with real developer app

## Slice 3 — Garmin and HA history
- [ ] HA entity mapping config screen / config options flow
- [ ] Normalize entity state and attributes to canonical metric samples
- [ ] Recorder history import with retention/availability disclosure
- [ ] Import Garmin export FIT/CSV/JSON where supported
- [ ] Per-source history coverage report

## Slice 4 — analytics
- [ ] Transparent 7-day and 42-day load model with tests
- [ ] Pace/HR efficiency trends by sport and conditions where available
- [ ] Readiness baseline based on personal history and data quality
- [ ] Plan adaptation proposal, confirmation and rollback
- [ ] Historical recalculation by algorithm version

## Slice 5 — Android native app
- [ ] Backend URL and API key setup in encrypted storage
- [ ] Retrofit client + repository + view models
- [ ] Dashboard, history, plan, trends, integrations
- [ ] Health Connect permissions and historical read where eligible
- [ ] WorkManager sync, cache, notification permissions
- [ ] Unit and instrumentation tests; signed debug APK

## Slice 6 — reliability and release
- [ ] Backup and restore rehearsal
- [ ] API auth/rate limiting/TLS deployment guide
- [ ] Home Assistant real installation test
- [ ] Android device test
- [ ] Privacy/data deletion/export controls
- [ ] AI/nutrition/GPX modules only after core reliability
