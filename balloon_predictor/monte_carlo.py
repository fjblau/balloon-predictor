"""Monte Carlo ensemble runner for landing-zone uncertainty."""
from __future__ import annotations

import asyncio

import numpy as np

from .models import Ensemble, LaunchParams
from .tawhiri import TawhiriClient


async def run_ensemble(
    client: TawhiriClient,
    base: LaunchParams,
    n: int = 100,
    ascent_sigma: float = 0.3,
    burst_sigma_m: float = 500,
    descent_sigma: float = 0.5,
    seed: int | None = None,
) -> Ensemble:
    """Perturb key parameters and aggregate landing distribution."""
    rng = np.random.default_rng(seed)
    ascents = rng.normal(base.ascent_rate_mps, ascent_sigma, n)
    bursts = rng.normal(base.burst_alt_m, burst_sigma_m, n)
    descents = rng.normal(base.descent_rate_mps, descent_sigma, n)

    async def one(i: int):
        p = base.model_copy(update={
            "ascent_rate_mps": max(0.5, float(ascents[i])),
            "burst_alt_m": max(5000.0, float(bursts[i])),
            "descent_rate_mps": max(0.5, float(descents[i])),
        })
        return await client.predict(p)

    trajectories = await asyncio.gather(*(one(i) for i in range(n)))

    landings = np.array([
        [t.landing.lat, t.landing.lon]
        for t in trajectories if t.landing is not None
    ])
    mean = landings.mean(axis=0)
    cov = np.cov(landings.T)

    return Ensemble(
        base_params=base,
        trajectories=list(trajectories),
        landing_mean_lat=float(mean[0]),
        landing_mean_lon=float(mean[1]),
        landing_cov=cov.tolist(),
    )
