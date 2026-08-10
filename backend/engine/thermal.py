"""Temperature-dependent stage development for the APDM biological core."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping


@dataclass(frozen=True, slots=True)
class ThermalPoint:
    temperature_c: float
    mean_duration_days: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.temperature_c):
            raise ValueError("temperature_c must be finite.")
        if not math.isfinite(self.mean_duration_days) or self.mean_duration_days <= 0:
            raise ValueError("mean_duration_days must be finite and > 0.")


def _linear_interpolate(
    points: tuple[tuple[float, float], ...],
    x: float,
) -> float:
    if not points:
        raise ValueError("At least one measured point is required.")

    if x <= points[0][0]:
        return points[0][1]

    if x >= points[-1][0]:
        return points[-1][1]

    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if x0 <= x <= x1:
            q = (x - x0) / (x1 - x0)
            return y0 + q * (y1 - y0)

    raise RuntimeError("Interpolation interval not found.")


class ThermalDevelopmentModel:
    """
    Temperature-dependent immature-stage development model.

    The initial implementation deliberately uses interpolation between
    estimable laboratory stage-duration measurements.

    Temperatures outside the measured range are clamped to the nearest
    measured value instead of being extrapolated. This is a conservative
    baseline until nonlinear thermal-response functions are independently
    validated.
    """

    def __init__(
        self,
        stage_parameters: Mapping[
            str,
            Mapping[str, Mapping[str, object]],
        ],
    ) -> None:
        self._duration_points: dict[
            str,
            tuple[tuple[float, float], ...],
        ] = {}

        for stage, by_temperature in stage_parameters.items():
            points: list[tuple[float, float]] = []

            for temperature, record in by_temperature.items():
                duration = record.get("mean_duration_days")

                if duration is None:
                    continue

                value = float(duration)

                if value <= 0 or not math.isfinite(value):
                    continue

                points.append(
                    (
                        float(temperature),
                        value,
                    )
                )

            if points:
                self._duration_points[stage] = tuple(sorted(points))

    @property
    def stages(self) -> tuple[str, ...]:
        """Return stages for which usable development data are available."""

        return tuple(self._duration_points)

    def mean_duration_days(
        self,
        stage: str,
        temperature_c: float,
    ) -> float:
        """
        Estimate mean stage duration at a constant temperature.
        """

        try:
            points = self._duration_points[stage]
        except KeyError as exc:
            raise KeyError(
                f"No estimable development data for stage {stage!r}."
            ) from exc

        return _linear_interpolate(
            points,
            float(temperature_c),
        )

    def daily_development_rate(
        self,
        stage: str,
        temperature_c: float,
    ) -> float:
        """
        Fraction of the mean stage duration completed in one day.
        """

        duration = self.mean_duration_days(
            stage,
            temperature_c,
        )

        return 1.0 / duration

    def four_point_daily_rate(
        self,
        stage: str,
        tmin_c: float,
        tmax_c: float,
    ) -> float:
        """
        Approximate development across a fluctuating day.

        Four temperatures are sampled from a sinusoidal daily temperature
        curve and the resulting development rates are averaged.
        """

        if tmin_c > tmax_c:
            raise ValueError(
                "tmin_c cannot exceed tmax_c."
            )

        mean = (tmin_c + tmax_c) / 2.0
        amplitude = max(
            0.0,
            (tmax_c - tmin_c) / 2.0,
        )

        phases = (
            0.125,
            0.375,
            0.625,
            0.875,
        )

        temperatures = tuple(
            mean
            + amplitude
            * math.sin(
                2.0 * math.pi * phase
                - math.pi / 2.0
            )
            for phase in phases
        )

        rates = [
            self.daily_development_rate(
                stage,
                temperature,
            )
            for temperature in temperatures
        ]

        return sum(rates) / len(rates)