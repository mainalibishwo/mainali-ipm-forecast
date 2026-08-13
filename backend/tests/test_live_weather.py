import pytest

from backend.api import SimulationRequest, simulate
from backend.engine.live_weather import _parse_daily, merge_weather
from backend.engine.weather import WeatherDay
from datetime import date


def test_parse_open_meteo_daily_payload():
    rows = _parse_daily({"daily": {
        "time": ["2026-08-13", "2026-08-14"],
        "temperature_2m_min": [9.0, 10.0],
        "temperature_2m_max": [21.0, 22.0],
        "precipitation_sum": [None, 3.5],
    }})
    assert len(rows) == 2
    assert rows[0].rainfall_mm == 0.0
    assert rows[1].tmax == 22.0


def test_live_weather_overwrites_same_stored_date():
    stored = [WeatherDay(date(2026, 8, 13), 8, 20, 0)]
    live = [WeatherDay(date(2026, 8, 13), 9, 22, 4)]
    merged = merge_weather(stored, live)
    assert len(merged) == 1
    assert merged[0].tmax == 22
    assert merged[0].rainfall_mm == 4


def test_live_weather_rejected_for_named_validation_series():
    with pytest.raises(Exception) as error:
        simulate(SimulationRequest(
            location="malua",
            weather_source="live",
            initialization="overwintering_adults",
            initial_eggs=0,
            initial_adult_females_by_age={0: 5},
            initial_adult_males_by_age={0: 5},
            seasonal_activation="central",
        ))
    assert "only for regional series" in str(error.value)
