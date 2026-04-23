"""Domain models shared across the library."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class LaunchParams(BaseModel):
    """Inputs for a single prediction run."""

    launch_lat: float = Field(..., ge=-90, le=90)
    launch_lon: float = Field(..., ge=-180, le=180)
    launch_alt_m: float = Field(0, ge=0)
    launch_time: datetime
    ascent_rate_mps: float = Field(..., gt=0)
    burst_alt_m: float = Field(..., gt=0)
    descent_rate_mps: float = Field(..., gt=0, description="Target rate at sea level")
    model: Literal["gfs"] = "gfs"


class TrajectoryPoint(BaseModel):
    t: datetime
    lat: float
    lon: float
    alt_m: float


class Trajectory(BaseModel):
    params: LaunchParams
    points: list[TrajectoryPoint]
    forecast_cycle: datetime | None = None
    landing: TrajectoryPoint | None = None
    burst: TrajectoryPoint | None = None


class Ensemble(BaseModel):
    """Result of a Monte Carlo run."""

    base_params: LaunchParams
    trajectories: list[Trajectory]
    landing_mean_lat: float
    landing_mean_lon: float
    landing_cov: list[list[float]]


class BalloonSpec(BaseModel):
    """Manufacturer balloon characteristics."""

    name: str
    mass_g: float
    burst_diameter_m: float
    drag_coefficient: float = 0.25
