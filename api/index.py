"""Vercel serverless entrypoint for balloon-predictor."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from balloon_predictor.burst import BurstResult, compute_burst, list_balloons
from balloon_predictor.models import LaunchParams, Trajectory
from balloon_predictor.tawhiri import TawhiriClient

app = FastAPI(
    title="balloon-predictor API",
    description="High-altitude balloon flight prediction — Tawhiri client, burst calculator.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"ok": True}


class BurstRequest(BaseModel):
    balloon: str
    payload_mass_kg: float
    target_ascent_rate_mps: float | None = None
    neck_lift_g: float | None = None


@app.get("/api/balloons")
async def balloons():
    return {"balloons": list_balloons()}


@app.post("/api/burst", response_model=BurstResult)
async def burst(req: BurstRequest):
    if req.balloon not in list_balloons():
        raise HTTPException(
            status_code=400,
            detail=f"Unknown balloon '{req.balloon}'. Available: {list_balloons()}",
        )
    try:
        result = compute_burst(
            balloon=req.balloon,
            payload_mass_kg=req.payload_mass_kg,
            target_ascent_rate_mps=req.target_ascent_rate_mps,
            neck_lift_g=req.neck_lift_g,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return result


@app.post("/api/predict", response_model=Trajectory)
async def predict(params: LaunchParams):
    client = TawhiriClient()
    try:
        return await client.predict(params)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    finally:
        await client.close()
