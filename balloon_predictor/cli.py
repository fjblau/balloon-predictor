"""`balloon-predict …` CLI for quick local checks."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone

import typer

from .models import LaunchParams
from .tawhiri import TawhiriClient

app = typer.Typer()


@app.command()
def predict(
    lat: float,
    lon: float,
    launch_iso: str = typer.Option(..., help="Launch time ISO-8601 UTC"),
    ascent: float = 5.0,
    burst: float = 30000,
    descent: float = 5.0,
    alt: float = 0,
):
    """Fire one prediction against the public Tawhiri instance."""
    params = LaunchParams(
        launch_lat=lat,
        launch_lon=lon,
        launch_alt_m=alt,
        launch_time=datetime.fromisoformat(launch_iso).astimezone(timezone.utc),
        ascent_rate_mps=ascent,
        burst_alt_m=burst,
        descent_rate_mps=descent,
    )

    async def go():
        c = TawhiriClient()
        try:
            t = await c.predict(params)
            print(f"Landing: {t.landing.lat:.5f}, {t.landing.lon:.5f}")
            print(f"Burst:   {t.burst.alt_m:.0f} m @ {t.burst.t.isoformat()}")
            print(f"Points:  {len(t.points)}")
        finally:
            await c.close()

    asyncio.run(go())


@app.command()
def burst(
    balloon: str = typer.Argument(help="Balloon type, e.g. hwoyee-1000"),
    payload: float = typer.Option(..., help="Payload mass in kg"),
    ascent: float = typer.Option(None, help="Target ascent rate m/s"),
    neck_lift: float = typer.Option(None, help="Neck lift in grams"),
):
    """Calculate burst altitude for a balloon + payload combination."""
    from .burst import compute_burst, list_balloons

    if balloon not in list_balloons():
        typer.echo(f"Unknown balloon. Available: {', '.join(list_balloons())}")
        raise typer.Exit(1)

    result = compute_burst(
        balloon=balloon,
        payload_mass_kg=payload,
        target_ascent_rate_mps=ascent,
        neck_lift_g=neck_lift,
    )
    print(f"Burst altitude:  {result.burst_altitude_m:.0f} m")
    print(f"Ascent rate:     {result.ascent_rate_mps:.2f} m/s")
    print(f"Neck lift:       {result.neck_lift_g:.1f} g")
    print(f"Helium mass:     {result.helium_mass_kg * 1000:.0f} g")


if __name__ == "__main__":
    app()
