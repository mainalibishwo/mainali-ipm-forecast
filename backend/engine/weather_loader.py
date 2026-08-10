"""
weather_loader.py

Load daily weather observations from CSV and convert them into WeatherDay
objects for the Mainali IPM Forecast Engine.
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from backend.engine.weather import WeatherDay


class WeatherLoader:
    """Load daily weather observations from CSV."""

    REQUIRED_COLUMNS = {
        "date",
        "tmin",
        "tmax",
    }

    @staticmethod
    def load_csv(csv_file: str | Path) -> list[WeatherDay]:

        csv_file = Path(csv_file)

        if not csv_file.exists():
            raise FileNotFoundError(csv_file)

        weather = []

        with csv_file.open("r", newline="") as f:

            reader = csv.DictReader(f)

            missing = WeatherLoader.REQUIRED_COLUMNS - set(reader.fieldnames or [])

            if missing:
                raise ValueError(
                    f"Missing required columns: {sorted(missing)}"
                )

            for row in reader:

                rainfall = row.get("rainfall_mm", "")

                weather.append(
                    WeatherDay(
                        weather_date=datetime.strptime(
                            row["date"],
                            "%Y-%m-%d",
                        ).date(),
                        tmin=float(row["tmin"]),
                        tmax=float(row["tmax"]),
                        rainfall_mm=float(rainfall) if rainfall else 0.0,
                    )
                )

        return weather