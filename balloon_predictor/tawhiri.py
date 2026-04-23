"""Async client for the Tawhiri prediction API.

Works against the public SondeHub instance (non-commercial only) or
a self-hosted Tawhiri — set `base_url` accordingly.
"""
from __future__ import annotations

from datetime import datetime

import httpx

from .models import LaunchParams, Trajectory, TrajectoryPoint


class TawhiriClient:
    def __init__(
        self,
        base_url: str = "https://api.v2.sondehub.org/tawhiri",
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(timeout=timeout)

    async def close(self) -> None:
        await self._client.aclose()

    async def predict(self, params: LaunchParams) -> Trajectory:
        payload = {
            "launch_latitude": params.launch_lat,
            "launch_longitude": params.launch_lon,
            "launch_altitude": params.launch_alt_m,
            "launch_datetime": params.launch_time.isoformat(),
            "ascent_rate": params.ascent_rate_mps,
            "burst_altitude": params.burst_alt_m,
            "descent_rate": params.descent_rate_mps,
            "profile": "standard_profile",
            "dataset": params.model,
        }
        r = await self._client.get(self.base_url, params=payload)
        r.raise_for_status()
        data = r.json()
        return self._parse(data, params)

    def _parse(self, data: dict, params: LaunchParams) -> Trajectory:
        points: list[TrajectoryPoint] = []
        burst: TrajectoryPoint | None = None

        for stage in data.get("prediction", []):
            for p in stage.get("trajectory", []):
                pt = TrajectoryPoint(
                    t=datetime.fromisoformat(p["datetime"].replace("Z", "+00:00")),
                    lat=p["latitude"],
                    lon=((p["longitude"] + 180) % 360) - 180,
                    alt_m=p["altitude"],
                )
                points.append(pt)
            if stage.get("stage") == "ascent" and points:
                burst = points[-1]

        landing = points[-1] if points else None
        cycle = None
        if "request" in data and "dataset" in data["request"]:
            try:
                cycle = datetime.fromisoformat(
                    data["request"]["dataset"].replace("Z", "+00:00")
                )
            except (ValueError, TypeError):
                pass

        return Trajectory(
            params=params,
            points=points,
            forecast_cycle=cycle,
            landing=landing,
            burst=burst,
        )
