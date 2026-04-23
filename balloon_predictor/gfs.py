"""GFS forecast cube fetcher.

Requires the optional `gfs` extras:
    pip install balloon-predictor[gfs]
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import xarray as xr

GFS_NOMADS_URL = (
    "https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod"
)


def latest_cycle() -> datetime:
    """Return the most recent available GFS cycle (UTC, 6-hourly)."""
    now = datetime.now(timezone.utc)
    cycle_hour = (now.hour // 6) * 6
    return now.replace(hour=cycle_hour, minute=0, second=0, microsecond=0)


def fetch_cube(
    lat_min: float,
    lat_max: float,
    lon_min: float,
    lon_max: float,
    cycle: datetime | None = None,
    cache_dir: Path | str | None = None,
) -> "xr.Dataset":
    """Download a sub-region of the GFS 0.25° analysis cube.

    Parameters
    ----------
    lat_min, lat_max, lon_min, lon_max:
        Bounding box for the spatial subset.
    cycle:
        GFS initialisation time (UTC). Defaults to `latest_cycle()`.
    cache_dir:
        Directory to cache downloaded GRIB2 files. No caching if None.

    Returns
    -------
    xarray.Dataset with variables ``u``, ``v``, ``gh`` on pressure levels.
    """
    try:
        import xarray as xr  # noqa: F401
        import cfgrib  # noqa: F401
    except ImportError as exc:
        raise ImportError(
            "GFS fetching requires the optional 'gfs' extras.\n"
            "Install with: pip install balloon-predictor[gfs]"
        ) from exc

    if cycle is None:
        cycle = latest_cycle()

    raise NotImplementedError(
        "GFS cube fetching is not yet implemented. "
        "Use the Tawhiri client for trajectory predictions."
    )
