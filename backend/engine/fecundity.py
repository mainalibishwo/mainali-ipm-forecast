"""
fecundity.py

Temperature- and age-dependent reproduction for the Mainali IPM Forecast Engine.

This module contains no hard-coded biological values. It reads measured
fecundity schedules from the biological parameter registry.
"""

from __future__ import annotations

import math
from typing import Mapping


def _linear_interpolate(
    points: tuple[tuple[float, float], ...],
    x: float,
) -> float:
    if not points:
        return 0.0

    if x <= points[0][0]:
        return points[0][1]

    if x >= points[-1][0]:
        return points[-1][1]

    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if x0 <= x <= x1:
            q = (x - x0) / (x1 - x0)
            return y0 + q * (y1 - y0)

    return points[-1][1]


class FecundityModel:
    """
    Age- and temperature-dependent female fecundity model.
    """

    def __init__(
        self,
        fecundity_by_temperature: Mapping[
            float,
            Mapping[int, float],
        ],
        reproductive_lower_limit_c: float,
        reproductive_upper_limit_c: float,
        maximum_adult_age_days: int,
    ) -> None:
        if reproductive_lower_limit_c >= reproductive_upper_limit_c:
            raise ValueError(
                "Lower reproductive limit must be below upper limit."
            )

        if maximum_adult_age_days <= 0:
            raise ValueError(
                "maximum_adult_age_days must be > 0."
            )

        self._fecundity = {
            float(temp): {
                int(age): float(value)
                for age, value in by_age.items()
            }
            for temp, by_age in fecundity_by_temperature.items()
        }

        self.lower_limit = float(reproductive_lower_limit_c)
        self.upper_limit = float(reproductive_upper_limit_c)
        self.maximum_age = int(maximum_adult_age_days)

    def eggs_per_female_day(
        self,
        temperature_c: float,
        female_age_days: int,
    ) -> float:
        """
        Return expected eggs per female per day.
        """

        if female_age_days < 0:
            raise ValueError(
                "female_age_days cannot be negative."
            )

        if temperature_c <= self.lower_limit:
            return 0.0

        if temperature_c >= self.upper_limit:
            return 0.0

        age = min(
            int(female_age_days),
            self.maximum_age,
        )

        temperature_points: list[tuple[float, float]] = []

        for temperature, by_age in self._fecundity.items():
            value = float(by_age.get(age, 0.0))

            if not math.isfinite(value) or value < 0:
                raise ValueError(
                    "Fecundity values must be finite and non-negative."
                )

            temperature_points.append(
                (
                    temperature,
                    value,
                )
            )

        temperature_points.sort()

        if not temperature_points:
            return 0.0

        lowest_measured = temperature_points[0][0]
        highest_measured = temperature_points[-1][0]

        # Below the lowest measured reproductive temperature,
        # taper linearly from zero at the biological lower limit.
        if temperature_c < lowest_measured:
            measured_value = temperature_points[0][1]

            fraction = (
                (temperature_c - self.lower_limit)
                / (lowest_measured - self.lower_limit)
            )

            return max(
                0.0,
                measured_value * fraction,
            )

        # Above the highest measured reproductive temperature,
        # taper linearly toward zero at the biological upper limit.
        if temperature_c > highest_measured:
            measured_value = temperature_points[-1][1]

            fraction = (
                (self.upper_limit - temperature_c)
                / (self.upper_limit - highest_measured)
            )

            return max(
                0.0,
                measured_value * fraction,
            )

        return max(
            0.0,
            _linear_interpolate(
                tuple(temperature_points),
                float(temperature_c),
            ),
        )

    def daily_egg_production(
        self,
        female_age_distribution: Mapping[int, float],
        temperature_c: float,
    ) -> float:
        """
        Calculate total eggs produced by all adult females in one day.
        """

        total_eggs = 0.0

        for age, females in female_age_distribution.items():
            if females < 0:
                raise ValueError(
                    "Female abundance cannot be negative."
                )

            total_eggs += (
                females
                * self.eggs_per_female_day(
                    temperature_c,
                    age,
                )
            )

        return total_eggs