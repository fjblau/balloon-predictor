"""Tests for the Tawhiri API client."""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from balloon_predictor.models import LaunchParams
from balloon_predictor.tawhiri import TawhiriClient


LAUNCH_PARAMS = LaunchParams(
    launch_lat=51.5,
    launch_lon=-1.8,
    launch_alt_m=100.0,
    launch_time=datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc),
    ascent_rate_mps=5.0,
    burst_alt_m=30000.0,
    descent_rate_mps=5.0,
)

SAMPLE_RESPONSE = {
    "prediction": [
        {
            "stage": "ascent",
            "trajectory": [
                {
                    "datetime": "2024-06-01T12:00:00Z",
                    "latitude": 51.5,
                    "longitude": 358.2,
                    "altitude": 100.0,
                },
                {
                    "datetime": "2024-06-01T14:00:00Z",
                    "latitude": 52.0,
                    "longitude": 357.5,
                    "altitude": 30000.0,
                },
            ],
        },
        {
            "stage": "descent",
            "trajectory": [
                {
                    "datetime": "2024-06-01T14:30:00Z",
                    "latitude": 52.3,
                    "longitude": 357.0,
                    "altitude": 0.0,
                },
            ],
        },
    ],
    "request": {
        "dataset": "2024-06-01T12:00:00Z",
    },
}


def _make_mock_response(data: dict, status: int = 200):
    response = MagicMock()
    response.json.return_value = data
    response.raise_for_status = MagicMock()
    response.status_code = status
    return response


@pytest.mark.asyncio
async def test_predict_returns_trajectory():
    client = TawhiriClient()
    mock_response = _make_mock_response(SAMPLE_RESPONSE)

    with patch.object(client._client, "get", new_callable=AsyncMock, return_value=mock_response):
        traj = await client.predict(LAUNCH_PARAMS)

    assert traj is not None
    assert len(traj.points) == 3
    assert traj.landing is not None
    assert traj.burst is not None


@pytest.mark.asyncio
async def test_predict_normalises_longitude():
    client = TawhiriClient()
    mock_response = _make_mock_response(SAMPLE_RESPONSE)

    with patch.object(client._client, "get", new_callable=AsyncMock, return_value=mock_response):
        traj = await client.predict(LAUNCH_PARAMS)

    for pt in traj.points:
        assert -180.0 <= pt.lon <= 180.0


@pytest.mark.asyncio
async def test_predict_sets_forecast_cycle():
    client = TawhiriClient()
    mock_response = _make_mock_response(SAMPLE_RESPONSE)

    with patch.object(client._client, "get", new_callable=AsyncMock, return_value=mock_response):
        traj = await client.predict(LAUNCH_PARAMS)

    assert traj.forecast_cycle is not None
    assert traj.forecast_cycle == datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)


@pytest.mark.asyncio
async def test_predict_burst_is_last_ascent_point():
    client = TawhiriClient()
    mock_response = _make_mock_response(SAMPLE_RESPONSE)

    with patch.object(client._client, "get", new_callable=AsyncMock, return_value=mock_response):
        traj = await client.predict(LAUNCH_PARAMS)

    assert traj.burst is not None
    assert traj.burst.alt_m == pytest.approx(30000.0)


@pytest.mark.asyncio
async def test_predict_empty_response():
    client = TawhiriClient()
    mock_response = _make_mock_response({"prediction": []})

    with patch.object(client._client, "get", new_callable=AsyncMock, return_value=mock_response):
        traj = await client.predict(LAUNCH_PARAMS)

    assert traj.points == []
    assert traj.landing is None
    assert traj.burst is None


@pytest.mark.asyncio
async def test_close():
    client = TawhiriClient()
    with patch.object(client._client, "aclose", new_callable=AsyncMock) as mock_close:
        await client.close()
        mock_close.assert_called_once()


def test_default_base_url():
    client = TawhiriClient()
    assert "sondehub.org" in client.base_url


def test_custom_base_url():
    client = TawhiriClient(base_url="https://tawhiri.example.com/tawhiri/")
    assert client.base_url == "https://tawhiri.example.com/tawhiri"
