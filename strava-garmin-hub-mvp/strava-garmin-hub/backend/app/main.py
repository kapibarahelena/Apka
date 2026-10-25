from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.config import settings
from app.db import Base, engine, get_db
from app.models import Activity, MetricSample, SourceConnection, PlannedWorkout
from app.credentials import new_oauth_state, consume_oauth_state, save_credentials, load_credentials, CredentialError
from app.security import require_api_key
from app.connectors.strava import StravaClient, StravaError, import_activities
from app.analytics.core import dashboard, load_summary, latest_metrics
import secrets

app = FastAPI(title="Szymon Training Hub API", version="0.1.0", description="Personal training analytics backend")
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.cors_origins.split(",") if x.strip()], allow_credentials=False, allow_methods=["GET", "POST", "PUT", "OPTIONS"], allow_headers=["Authorization", "Content-Type", "X-Hub-API-Key"])
# MVP convenience. Production should use Alembic migrations; see docs/ARCHITECTURE.md.
@app.on_event("startup")
def startup(): Base.metadata.create_all(bind=engine)

@app.get("/health")
def health(): return {"status": "ok", "service": "training-hub-api", "version": app.version}

@app.get("/api/v1/dashboard", dependencies=[Depends(require_api_key)])
def get_dashboard(db: Session = Depends(get_db)): return dashboard(db)

@app.get("/api/v1/activities", dependencies=[Depends(require_api_key)])
def list_activities(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    limit = min(max(limit, 1), 200)
    rows = db.scalars(select(Activity).order_by(Activity.started_at.desc()).offset(max(offset, 0)).limit(limit)).all()
    count = db.scalar(select(func.count()).select_from(Activity)) or 0
    return {"total": count, "limit": limit, "offset": max(offset, 0), "items": [{"id": a.id, "source": a.source, "source_id": a.source_id, "name": a.name, "sport_type": a.sport_type, "started_at": a.started_at.isoformat(), "elapsed_seconds": a.elapsed_seconds, "distance_m": a.distance_m, "average_hr": a.average_hr} for a in rows]}

@app.get("/api/v1/metrics/daily", dependencies=[Depends(require_api_key)])
def get_metrics(db: Session = Depends(get_db)): return {"items": latest_metrics(db)}

@app.get("/api/v1/analytics/load", dependencies=[Depends(require_api_key)])
def get_load(db: Session = Depends(get_db)): return load_summary(db)

@app.get("/api/v1/integrations/status", dependencies=[Depends(require_api_key)])
def integration_status(db: Session = Depends(get_db)):
    rows = db.scalars(select(SourceConnection)).all()
    known = {r.source: r for r in rows}
    return {"items": [{"source": source, "status": known[source].status if source in known else "not_configured", "last_success_at": known[source].last_success_at.isoformat() if source in known and known[source].last_success_at else None, "last_error": known[source].last_error if source in known else None, "history_start": known[source].history_start.isoformat() if source in known and known[source].history_start else None, "history_end": known[source].history_end.isoformat() if source in known and known[source].history_end else None} for source in ["strava", "home_assistant", "health_connect", "garmin_export"]]}

@app.get("/api/v1/connections/strava/authorize", dependencies=[Depends(require_api_key)])
def strava_authorize(db: Session = Depends(get_db)):
    try:
        state = new_oauth_state(db)
        return {"authorization_url": StravaClient().authorization_url(state), "note": "Open authorization_url in a browser and approve requested scopes."}
    except (StravaError, CredentialError) as exc:
        raise HTTPException(503, detail=str(exc))

@app.get("/api/v1/connections/strava/callback")
def strava_callback(code: str | None = None, error: str | None = None, state: str | None = None, db: Session = Depends(get_db)):
    if error: raise HTTPException(400, detail=f"Strava authorization denied: {error}")
    if not code or not state: raise HTTPException(400, detail="Missing OAuth code or state")
    if not consume_oauth_state(db, state): raise HTTPException(400, detail="Invalid or expired OAuth state")
    try:
        token_data = StravaClient().exchange_code(code)
        save_credentials(db, "strava", token_data)
        conn = db.scalar(select(SourceConnection).where(SourceConnection.source == "strava"))
        if not conn: db.add(SourceConnection(source="strava", status="connected"))
        else: conn.status, conn.last_error = "connected", None
        db.commit()
        return {"status": "connected", "athlete_id": token_data.get("athlete", {}).get("id"), "message": "Strava połączona. Token zapisano w zaszyfrowanej postaci."}
    except (StravaError, CredentialError) as exc:
        raise HTTPException(502, detail=str(exc))

@app.post("/api/v1/sync/strava", dependencies=[Depends(require_api_key)])
def sync_strava(db: Session = Depends(get_db)):
    try:
        token = load_credentials(db, "strava")
        if not token: raise HTTPException(409, detail="Strava is not connected; call /api/v1/connections/strava/authorize first")
        client = StravaClient()
        refreshed = client.refresh(token["refresh_token"])
        save_credentials(db, "strava", refreshed)
        result = import_activities(db, client, refreshed["access_token"], page_size=settings.sync_page_size)
        return result
    except HTTPException: raise
    except (StravaError, CredentialError) as exc:
        conn = db.scalar(select(SourceConnection).where(SourceConnection.source == "strava"))
        if conn: conn.status, conn.last_error = "error", str(exc); db.commit()
        raise HTTPException(502, detail=str(exc))

@app.get("/api/v1/plan", dependencies=[Depends(require_api_key)])
def get_plan(db: Session = Depends(get_db)):
    rows = db.scalars(select(PlannedWorkout).order_by(PlannedWorkout.scheduled_date)).all()
    return {"items": [{"id": x.id, "plan_id": x.plan_id, "scheduled_date": x.scheduled_date, "title": x.title, "sport": x.sport, "status": x.status, "duration_minutes": x.duration_minutes, "intensity": x.intensity, "adaptation_reason": x.adaptation_reason, "version": x.version} for x in rows]}

@app.post("/api/v1/plan/workouts/{workout_id}/{action}", dependencies=[Depends(require_api_key)])
def update_workout(workout_id: int, action: str, db: Session = Depends(get_db)):
    if action not in ("complete", "skip"): raise HTTPException(404, detail="Action must be complete or skip")
    row = db.get(PlannedWorkout, workout_id)
    if not row: raise HTTPException(404, detail="Workout not found")
    row.status = "completed" if action == "complete" else "skipped"
    row.version += 1
    db.commit()
    return {"id": row.id, "status": row.status, "version": row.version, "adaptation": "Plan recalculation is queued for the next implementation slice."}
