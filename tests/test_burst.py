"""Tests for burst altitude and helium calculators."""
import math

import pytest

from balloon_predictor.burst import BurstResult, compute_burst, list_balloons


def test_list_balloons_returns_known_types():
    balloons = list_balloons()
    assert "hwoyee-1000" in balloons
    assert "hwoyee-1600" in balloons
    assert len(balloons) >= 4


def test_compute_burst_unknown_balloon():
    with pytest.raises(KeyError, match="Unknown balloon type"):
        compute_burst("nonexistent-9000", payload_mass_kg=1.0, target_ascent_rate_mps=5.0)


def test_compute_burst_requires_exactly_one_arg():
    with pytest.raises(ValueError, match="Specify exactly one"):
        compute_burst("hwoyee-1000", payload_mass_kg=1.0)

    with pytest.raises(ValueError, match="Specify exactly one"):
        compute_burst(
            "hwoyee-1000",
            payload_mass_kg=1.0,
            target_ascent_rate_mps=5.0,
            neck_lift_g=100.0,
        )


def test_compute_burst_with_ascent_rate():
    result = compute_burst(
        balloon="hwoyee-1000",
        payload_mass_kg=1.0,
        target_ascent_rate_mps=5.0,
    )
    assert isinstance(result, BurstResult)
    assert result.ascent_rate_mps == pytest.approx(5.0)
    assert result.burst_altitude_m > 0
    assert result.neck_lift_g > 0
    assert result.helium_mass_kg > 0


def test_compute_burst_with_neck_lift():
    result = compute_burst(
        balloon="hwoyee-1000",
        payload_mass_kg=1.0,
        neck_lift_g=1500.0,
    )
    assert isinstance(result, BurstResult)
    assert result.neck_lift_g == pytest.approx(1500.0)
    assert result.ascent_rate_mps > 0
    assert result.burst_altitude_m > 0


def test_compute_burst_higher_ascent_gives_more_lift():
    slow = compute_burst("hwoyee-1000", payload_mass_kg=1.0, target_ascent_rate_mps=3.0)
    fast = compute_burst("hwoyee-1000", payload_mass_kg=1.0, target_ascent_rate_mps=6.0)
    assert fast.neck_lift_g > slow.neck_lift_g


def test_compute_burst_returns_finite_values():
    result = compute_burst("totex-1500", payload_mass_kg=0.5, target_ascent_rate_mps=4.0)
    assert math.isfinite(result.burst_altitude_m)
    assert math.isfinite(result.ascent_rate_mps)
    assert math.isfinite(result.neck_lift_g)
    assert math.isfinite(result.helium_mass_kg)
