"""
weather.py

Weather data structures for the Mainali IPM Forecast Engine (MIFE).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum


class WeatherSource(str, Enum):
    """Origin of the weather record."""

    OBSERVED = "observed"
    FORECAST = "forecast"
    CLIMATOLOGY = "climatology"


@dataclass(frozen=True)
class WeatherDay:
    """
    Daily weather used by the biological simulation.
    """

    weather_date: date

    tmin: float
    tmax: float

    rainfall_mm: float = 0.0

    source: WeatherSource = WeatherSource.OBSERVED

    def __post_init__(self):

        if self.tmin > self.tmax:
            raise ValueError("Minimum temperature cannot exceed maximum temperature.")

        if self.rainfall_mm < 0:
            raise ValueError("Rainfall cannot be negative.")

    @property
    def mean_temperature(self) -> float:
        return (self.tmin + self.tmax) / 2.0

    @property
    def diurnal_range(self) -> float:
        return self.tmax - self.tmin

    def as_dict(self):

        return {
            "date": self.weather_date.isoformat(),
            "tmin": self.tmin,
            "tmax": self.tmax,
            "tmean": self.mean_temperature,
            "rainfall_mm": self.rainfall_mm,
            "source": self.source.value,
        }