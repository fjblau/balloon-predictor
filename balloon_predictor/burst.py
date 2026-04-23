"""Burst altitude and helium mass calculators.

Port of the CUSF burst calculator empirical model. The coefficient
tables below are placeholders — pull the real values from
https://github.com/jonsowman/cusf-standalone-predictor/blob/master/burst-calc.js
before relying on this in production.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

HELIUM_DENSITY_KG_M3 = 0.1786
AIR_DENSITY_KG_M3 = 1.2250
GRAVITY = 9.80665


@dataclass(frozen=True)
class BurstResult:
    burst_altitude_m: float
    ascent_rate_mps: float
    neck_lift_g: float
    helium_mass_kg: float


_BALLOON_BURST_COEFFICIENTS: dict[str, tuple[float, float]] = {
    "hwoyee-1000": (7.86, 0.25),
    "hwoyee-1600": (10.54, 0.25),
    "totex-1500": (9.44, 0.25),
    "totex-2000": (10.54, 0.25),
}


def compute_burst(
    balloon: str,
    payload_mass_kg: float,
    target_ascent_rate_mps: float | None = None,
    neck_lift_g: float | None = None,
) -> BurstResult:
    """Compute burst altitude given balloon type + payload.

    You must specify exactly one of target_ascent_rate_mps or neck_lift_g.
    """
    if (target_ascent_rate_mps is None) == (neck_lift_g is None):
        raise ValueError("Specify exactly one of target_ascent_rate_mps or neck_lift_g")

    if balloon not in _BALLOON_BURST_COEFFICIENTS:
        raise KeyError(f"Unknown balloon type: {balloon}")

    burst_d, cd = _BALLOON_BURST_COEFFICIENTS[balloon]

    if target_ascent_rate_mps is not None:
        ascent = target_ascent_rate_mps
        lift_n = (
            0.5 * AIR_DENSITY_KG_M3 * cd * math.pi * 1.0**2 * ascent**2
            + payload_mass_kg * GRAVITY
        )
        neck_lift_g = (lift_n / GRAVITY - payload_mass_kg) * 1000
    else:
        assert neck_lift_g is not None
        lift_kg = neck_lift_g / 1000
        ascent = math.sqrt(
            (lift_kg * GRAVITY)
            / (0.5 * AIR_DENSITY_KG_M3 * cd * math.pi * 1.0**2)
        )

    volume_at_burst = (4.0 / 3.0) * math.pi * (burst_d / 2) ** 3
    volume_at_launch = (neck_lift_g / 1000 + payload_mass_kg) / HELIUM_DENSITY_KG_M3
    pressure_ratio = volume_at_launch / volume_at_burst
    burst_alt = -7000.0 * math.log(pressure_ratio)

    helium_mass_kg = volume_at_launch * HELIUM_DENSITY_KG_M3

    return BurstResult(
        burst_altitude_m=burst_alt,
        ascent_rate_mps=ascent,
        neck_lift_g=neck_lift_g,
        helium_mass_kg=helium_mass_kg,
    )


def list_balloons() -> list[str]:
    return list(_BALLOON_BURST_COEFFICIENTS.keys())
