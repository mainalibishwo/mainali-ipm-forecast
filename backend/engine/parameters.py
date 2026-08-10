"""
parameters.py

Scientific parameter registry for the Mainali IPM Forecast Engine (MIFE).

The registry separates biological evidence from model algorithms.
Measured parameters can be locked, while estimated or scenario parameters
remain explicitly identifiable.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Mapping, Optional


class ParameterSource(str, Enum):
    """Evidence source for a model parameter."""

    LABORATORY = "laboratory"
    FIELD = "field"
    LITERATURE = "literature"
    CALIBRATION = "calibration"
    ASSUMPTION = "assumption"


class ParameterStatus(str, Enum):
    """How a parameter is treated by the forecasting engine."""

    MEASURED_LOCKED = "measured_locked"
    ESTIMATED = "estimated"
    SCENARIO = "scenario"


@dataclass(frozen=True, slots=True)
class ParameterMetadata:
    """Scientific provenance for one model parameter."""

    name: str
    source: ParameterSource
    status: ParameterStatus
    reference: Optional[str] = None
    notes: Optional[str] = None


@dataclass(frozen=True, slots=True)
class StageThermalRecord:
    """
    Thermal biology record for one immature stage at one temperature.
    """

    mean_duration_days: Optional[float] = None
    conditional_survival: Optional[float] = None

    def __post_init__(self) -> None:
        if self.mean_duration_days is not None:
            if self.mean_duration_days <= 0:
                raise ValueError(
                    "mean_duration_days must be > 0."
                )

        if self.conditional_survival is not None:
            if not 0.0 <= self.conditional_survival <= 1.0:
                raise ValueError(
                    "conditional_survival must be between 0 and 1."
                )


@dataclass(frozen=True)
class BiologicalParameterRegistry:
    """
    Versioned biological parameter registry.

    stage_parameters:
        Mapping of stage -> temperature -> StageThermalRecord.

    adult_female_survival_by_age:
        Mapping of temperature -> age (days) -> conditional survival.

    fecundity_eggs_per_female_day:
        Mapping of temperature -> female age (days) -> eggs/female/day.
    """

    species: str
    version: str

    stage_parameters: Mapping[
        str,
        Mapping[float, StageThermalRecord],
    ]

    adult_female_survival_by_age: Mapping[
        float,
        Mapping[int, float],
    ]

    fecundity_eggs_per_female_day: Mapping[
        float,
        Mapping[int, float],
    ]

    female_proportion: float

    reproductive_lower_limit_c: float
    reproductive_upper_limit_c: float

    maximum_adult_age_days: int

    metadata: Mapping[str, ParameterMetadata]

    def __post_init__(self) -> None:
        if not self.species.strip():
            raise ValueError("species cannot be empty.")

        if not self.version.strip():
            raise ValueError("version cannot be empty.")

        if not 0.0 < self.female_proportion < 1.0:
            raise ValueError(
                "female_proportion must be between 0 and 1."
            )

        if (
            self.reproductive_lower_limit_c
            >= self.reproductive_upper_limit_c
        ):
            raise ValueError(
                "reproductive lower limit must be below upper limit."
            )

        if self.maximum_adult_age_days <= 0:
            raise ValueError(
                "maximum_adult_age_days must be > 0."
            )

    @property
    def stages(self) -> tuple[str, ...]:
        """Return immature stages available in the registry."""

        return tuple(self.stage_parameters.keys())

    def stage_record(
        self,
        stage: str,
        temperature_c: float,
    ) -> StageThermalRecord:
        """
        Return an exact stage-temperature record.

        This method deliberately does not interpolate.
        Interpolation belongs in the biological calculation modules.
        """

        try:
            return self.stage_parameters[stage][temperature_c]
        except KeyError as exc:
            raise KeyError(
                f"No exact parameter record for stage={stage!r}, "
                f"temperature={temperature_c!r}."
            ) from exc


def registry_to_thermal_mapping(
    registry: BiologicalParameterRegistry,
) -> Dict[str, Dict[str, Dict[str, float | None]]]:
    """
    Convert the registry into the mapping expected by ThermalDevelopmentModel.

    This small adapter keeps thermal.py independent of the registry class.
    """

    result: Dict[
        str,
        Dict[str, Dict[str, float | None]],
    ] = {}

    for stage, by_temperature in registry.stage_parameters.items():
        result[stage] = {}

        for temperature, record in by_temperature.items():
            result[stage][str(temperature)] = {
                "mean_duration_days": record.mean_duration_days,
                "conditional_survival": record.conditional_survival,
            }

    return result