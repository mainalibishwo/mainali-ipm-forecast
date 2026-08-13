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


class SmoothDaylengthActivation:
    """A preregistered day-length sensitivity curve.

    The curve is an uncertainty scenario, not a fitted biological
    parameter.  It uses a smoothstep transition so that reproduction
    does not switch on at an arbitrary calendar date.  Temperature is
    deliberately not used here because it already controls the frozen
    fecundity surface.
    """

    def __init__(
        self,
        latitude_degrees: float,
        lower_daylength_hours: float,
        upper_daylength_hours: float,
        winter_floor: float = 0.0,
    ) -> None:
        if not -90.0 <= latitude_degrees <= 90.0:
            raise ValueError("Latitude must be between -90 and 90 degrees.")
        if not 0.0 <= lower_daylength_hours < upper_daylength_hours <= 24.0:
            raise ValueError("Day-length bounds must increase within 0–24 hours.")
        if not 0.0 <= winter_floor <= 1.0:
            raise ValueError("winter_floor must be between 0 and 1.")

        self.latitude_degrees = float(latitude_degrees)
        self.lower_daylength_hours = float(lower_daylength_hours)
        self.upper_daylength_hours = float(upper_daylength_hours)
        self.winter_floor = float(winter_floor)

    def activation(
        self,
        calendar_date: date,
        temperature_c: float,
    ) -> float:
        del temperature_c
        daylight = daylength_hours(calendar_date, self.latitude_degrees)

        if daylight <= self.lower_daylength_hours:
            return self.winter_floor
        if daylight >= self.upper_daylength_hours:
            return 1.0

        fraction = (
            (daylight - self.lower_daylength_hours)
            / (self.upper_daylength_hours - self.lower_daylength_hours)
        )
        smoothstep = fraction * fraction * (3.0 - 2.0 * fraction)
        return self.winter_floor + (1.0 - self.winter_floor) * smoothstep


DAYLENGTH_SENSITIVITY_PROFILES = {
    # Qualitative envelope constrained before field validation from
    # Waite (2000): reproduction virtually ceased in winter and rose
    # smoothly as the seasonal day-length/temperature signal increased.
    # These alternatives must be reported together, not selected using
    # Malua, Knockrow or Dorey agreement.
    "conservative": {
        "lower_daylength_hours": 11.00,
        "upper_daylength_hours": 12.25,
        "winter_floor": 0.00,
    },
    "central": {
        "lower_daylength_hours": 10.75,
        "upper_daylength_hours": 12.00,
        "winter_floor": 0.025,
    },
    "permissive": {
        "lower_daylength_hours": 10.50,
        "upper_daylength_hours": 11.75,
        "winter_floor": 0.05,
    },
}


def build_daylength_sensitivity_profile(
    profile: str,
    latitude_degrees: float,
) -> SmoothDaylengthActivation:
    """Construct one frozen member of the preregistered envelope."""

    try:
        values = DAYLENGTH_SENSITIVITY_PROFILES[profile]
    except KeyError as exc:
        raise ValueError(f"Unknown seasonal activation profile: {profile}") from exc

    return SmoothDaylengthActivation(
        latitude_degrees=latitude_degrees,
        **values,
    )


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
