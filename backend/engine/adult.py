"""
adult.py

Age-structured adult survival for the Mainali IPM Forecast Engine (MIFE).

Adult females and males are represented by daily age classes.
The model can use measured age-specific survival schedules and interpolate
across temperature when required.
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


class AdultSurvivalModel:
    """
    Age- and temperature-dependent adult survival model.
    """

    def __init__(
        self,
        survival_by_temperature: Mapping[
            float,
            Mapping[int, float],
        ],
        maximum_age_days: int,
    ) -> None:
        if maximum_age_days <= 0:
            raise ValueError(
                "maximum_age_days must be > 0."
            )

        self.maximum_age_days = int(maximum_age_days)

        self._survival = {
            float(temp): {
                int(age): float(value)
                for age, value in by_age.items()
            }
            for temp, by_age in survival_by_temperature.items()
        }

        for temp, by_age in self._survival.items():
            for age, value in by_age.items():
                if not math.isfinite(value):
                    raise ValueError(
                        f"Non-finite survival value at {temp}°C, age {age}."
                    )

                if not 0.0 <= value <= 1.0:
                    raise ValueError(
                        "Adult survival probabilities must lie between 0 and 1."
                    )

    def conditional_survival(
        self,
        temperature_c: float,
        age_days: int,
    ) -> float:
        """
        Return one-day conditional survival for a given age and temperature.
        """

        if age_days < 0:
            raise ValueError(
                "age_days cannot be negative."
            )

        age = min(
            int(age_days),
            self.maximum_age_days,
        )

        points = []

        for temperature, by_age in self._survival.items():
            points.append(
                (
                    temperature,
                    float(by_age.get(age, 0.0)),
                )
            )

        points.sort()

        return max(
            0.0,
            min(
                1.0,
                _linear_interpolate(
                    tuple(points),
                    float(temperature_c),
                ),
            ),
        )

    def age_one_day(
        self,
        age_distribution: Mapping[int, float],
        temperature_c: float,
    ) -> dict[int, float]:
        """
        Advance an adult age distribution by one day with survival.
        """

        next_distribution = {
            age: 0.0
            for age in range(self.maximum_age_days + 1)
        }

        for age, abundance in age_distribution.items():
            if abundance < 0:
                raise ValueError(
                    "Adult abundance cannot be negative."
                )

            if age < 0:
                raise ValueError(
                    "Adult age cannot be negative."
                )

            if age >= self.maximum_age_days:
                continue

            survival = self.conditional_survival(
                temperature_c,
                age,
            )

            next_distribution[age + 1] += (
                abundance * survival
            )

        return next_distribution

    @staticmethod
    def total_adults(
        age_distribution: Mapping[int, float],
    ) -> float:
        """Return total adults across all age classes."""

        return sum(age_distribution.values())