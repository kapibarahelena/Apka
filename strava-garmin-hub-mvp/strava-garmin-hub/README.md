# Szymon Training Hub

Personal sports analytics hub: Strava + Garmin/Home Assistant + native Android. The backend is the source of truth; clients do not calculate separate versions of analytics.

## Repository layout
- `backend/` FastAPI API, PostgreSQL schema, Strava OAuth/import and deterministic analytics.
- `homeassistant/custom_components/szymon_training_hub/` Home Assistant custom integration (config flow + API-backed sensors).
- `android/` native Kotlin + Jetpack Compose starter.
- `deploy/` Docker Compose and environment template.
- `docs/` technical decisions, API contract, history/backfill and the original HTML source for reference.

## Run the backend locally
1. Copy `deploy/.env.example` to `deploy/.env` and set `HUB_API_KEY` and database credentials.
2. From `deploy/`: `docker compose up --build`.
3. API docs: `http://localhost:8000/docs`; health: `http://localhost:8000/health`.

The API port is published to the host so Home Assistant on the same trusted LAN can reach it; do not expose it directly to the public Internet. Use HTTPS/reverse proxy and firewall rules for remote access. The Strava connector requires your own Strava API application credentials. Configure them only in the backend environment, never in Android or Home Assistant sensor attributes. See `docs/STRAVA_SETUP.md`.

## Current status
This is the first implementation scaffold, not a claim that external account connections have been verified. Strava import needs user credentials; Garmin history depends on the access path available in your account/integration. Android needs an installed Android SDK to build the APK. Run `backend/scripts/check.sh` or `pytest` after installing dependencies.
