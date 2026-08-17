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


def test_parse_open_meteo_trims_incomplete_forecast_tail():
    rows = _parse_daily({"daily": {
        "time": ["2026-08-29", "2026-08-30", "2026-08-31"],
        "temperature_2m_min": [10.0, 11.0, None],
        "temperature_2m_max": [22.0, 23.0, None],
        "precipitation_sum": [0.0, 1.0, None],
    }})
    assert [row.weather_date.isoformat() for row in rows] == [
        "2026-08-29",
        "2026-08-30",
    ]


def test_parse_open_meteo_rejects_payload_without_temperature():
    with pytest.raises(ValueError, match="no complete daily temperature"):
        _parse_daily({"daily": {
            "time": ["2026-08-31"],
            "temperature_2m_min": [None],
            "temperature_2m_max": [None],
            "precipitation_sum": [None],
        }})


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
