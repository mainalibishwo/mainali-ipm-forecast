from pathlib import Path

import pytest

from backend.engine.weather_loader import WeatherLoader


SAMPLE_WEATHER = Path("data/weather/sample_weather.csv")


def test_weather_loader_reads_all_rows():
    weather = WeatherLoader.load_csv(SAMPLE_WEATHER)

    assert len(weather) == 5


def test_weather_loader_parses_first_record():
    weather = WeatherLoader.load_csv(SAMPLE_WEATHER)

    first = weather[0]

    assert first.weather_date.isoformat() == "2026-08-01"
    assert first.tmin == 12.1
    assert first.tmax == 24.8
    assert first.rainfall_mm == 0.0

    assert first.mean_temperature == pytest.approx(18.45)


def test_weather_loader_preserves_order():
    weather = WeatherLoader.load_csv(SAMPLE_WEATHER)

    dates = [
        record.weather_date
        for record in weather
    ]

    assert dates == sorted(dates)


def test_weather_loader_missing_file():
    with pytest.raises(FileNotFoundError):
        WeatherLoader.load_csv(
            "data/weather/does_not_exist.csv"
        )


def test_weather_loader_missing_required_column(tmp_path):
    path = tmp_path / "bad_weather.csv"

    path.write_text(
        "date,tmin,rainfall_mm\n"
        "2026-08-01,12.0,0\n"
    )

    with pytest.raises(
        ValueError,
        match="Missing required columns",
    ):
        WeatherLoader.load_csv(path)


def test_blank_rainfall_becomes_zero(tmp_path):
    path = tmp_path / "weather.csv"

    path.write_text(
        "date,tmin,tmax,rainfall_mm\n"
        "2026-08-01,12,25,\n"
    )

    weather = WeatherLoader.load_csv(path)

    assert weather[0].rainfall_mm == 0.0