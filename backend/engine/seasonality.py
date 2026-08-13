"""Seasonal reproductive activation support for MIFE.

This module deliberately contains no fitted Amblypelta suppression
parameters.  It provides the bounded interface needed to keep seasonal
activation separate from the frozen age- and temperature-specific
fecundity model.
"""

from __future__ import annotations

import math
from datetime import date
from typing import Protocol


def daylength_hours(
    calendar_date: date,
    latitude_degrees: float,
) -> float:
    """Calculate astronomical day length for a date and latitude.

    The calculation uses solar declination and standard sunrise/sunset
    geometry.  It is an environmental covariate, not a biological
    parameter.
    """

    if not -90.0 <= latitude_degrees <= 90.0:
        raise ValueError("Latitude must be between -90 and 90 degrees.")

    day_of_year = calendar_date.timetuple().tm_yday
    latitude = math.radians(latitude_degrees)
    declination = math.radians(
        23.44
        * math.sin(
            2.0 * math.pi * (284 + day_of_year) / 365.0
        )
    )
    cosine_hour_angle = -math.tan(latitude) * math.tan(declination)

    if cosine_hour_angle >= 1.0:
        return 0.0
    if cosine_hour_angle <= -1.0:
        return 24.0

    hour_angle = math.acos(cosine_hour_angle)
    return 24.0 * hour_angle / math.pi


class ReproductiveActivationModel(Protocol):
    """Interface for an independently supported seasonal activation model."""

    def activation(
        self,
        calendar_date: date,
        temperature_c: float,
    ) -> float:
        """Return a bounded multiplier from 0 (suppressed) to 1 (active)."""


class NoSeasonalSuppression:
    """Reference behaviour that preserves the frozen MIFE v0.1 core."""

    def activation(
        self,
        calendar_date: date,
        temperature_c: float,
    ) -> float:
        del calendar_date, temperature_c
        return 1.0


def bounded_activation(
    model: ReproductiveActivationModel,
    calendar_date: date,
    temperature_c: float,
) -> float:
    """Evaluate an activation model and reject values outside [0, 1]."""

    value = float(model.activation(calendar_date, temperature_c))
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError(
            "Reproductive activation must be finite and between 0 and 1."
        )
    return value
