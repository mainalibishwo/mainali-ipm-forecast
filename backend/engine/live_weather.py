"""Live regional weather adapter for operational MIFE forecasts."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from threading import Lock
from time import monotonic
from urllib.parse import urlencode
from urllib.request import urlopen

from backend.engine.weather import WeatherDay


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
CACHE_SECONDS = 15 * 60
_cache: dict[tuple[float, float], tuple[float, list[WeatherDay], dict]] = {}
_cache_lock = Lock()


def _parse_daily(payload: dict) -> list[WeatherDay]:
    daily = payload.get("daily", {})
    fields = (
        daily.get("time", []),
        daily.get("temperature_2m_min", []),
        daily.get("temperature_2m_max", []),
        daily.get("precipitation_sum", []),
    )
    if not fields[0] or len({len(values) for values in fields}) != 1:
        raise ValueError("Live weather response contains incomplete daily data.")
    rows = []
    for day, tmin, tmax, rain in zip(*fields):
        # Open-Meteo can publish the final forecast date before every daily
        # aggregate has been populated.  A null temperature cannot drive the
        # biological engine, so stop at the last continuous complete day
        # rather than failing the whole live forecast or creating a date gap.
        if tmin is None or tmax is None:
            break
        rows.append(
            WeatherDay(
                weather_date=datetime.strptime(day, "%Y-%m-%d").date(),
                tmin=float(tmin),
                tmax=float(tmax),
                rainfall_mm=float(rain or 0.0),
            )
        )
    if not rows:
        raise ValueError(
            "Live weather response contains no complete daily temperature data."
        )
    return rows


def fetch_open_meteo(
    latitude: float,
    longitude: float,
    *,
    past_days: int = 10,
    forecast_days: int = 16,
) -> tuple[list[WeatherDay], dict]:
    """Fetch recent and forecast daily weather, cached for 15 minutes."""

    key = (float(latitude), float(longitude))
    with _cache_lock:
        cached = _cache.get(key)
        if cached and monotonic() - cached[0] < CACHE_SECONDS:
            return list(cached[1]), dict(cached[2])

    query = urlencode({
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_min,temperature_2m_max,precipitation_sum",
        "timezone": "Australia/Sydney",
        "past_days": past_days,
        "forecast_days": forecast_days,
    })
    # Serialize a cache miss so the nine-scenario dashboard ensemble makes one
    # provider request rather than nine concurrent requests for the same point.
    with _cache_lock:
        cached = _cache.get(key)
        if cached and monotonic() - cached[0] < CACHE_SECONDS:
            return list(cached[1]), dict(cached[2])
        with urlopen(f"{OPEN_METEO_URL}?{query}", timeout=15) as response:
            payload = json.load(response)
        rows = _parse_daily(payload)
        metadata = {
            "provider": "Open-Meteo",
            "provider_url": "https://open-meteo.com/",
            "model_selection": "best_match",
            "latitude": float(payload.get("latitude") or latitude),
            "longitude": float(payload.get("longitude") or longitude),
            "timezone": payload.get("timezone", "Australia/Sydney"),
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
            "forecast_end": rows[-1].weather_date.isoformat(),
        }
        _cache[key] = (monotonic(), list(rows), dict(metadata))
    return rows, metadata


def merge_weather(
    stored: list[WeatherDay],
    live: list[WeatherDay],
) -> list[WeatherDay]:
    """Merge by date, preferring recent/live values on overlapping dates."""

    by_date = {row.weather_date: row for row in stored}
    by_date.update({row.weather_date: row for row in live})
    return [by_date[day] for day in sorted(by_date)]
