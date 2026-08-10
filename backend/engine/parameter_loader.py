"""
parameter_loader.py

Load and validate biological parameter datasets for the
Mainali IPM Forecast Engine (MIFE).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from backend.engine.parameters import (
    BiologicalParameterRegistry,
    ParameterMetadata,
    ParameterSource,
    ParameterStatus,
    StageThermalRecord,
)


REQUIRED_THERMAL_COLUMNS = {
    "stage",
    "temperature_c",
    "mean_duration_days",
    "conditional_survival",
}

REQUIRED_FECUNDITY_COLUMNS = {
    "temperature_c",
    "female_age_days",
    "eggs_per_female_day",
}

REQUIRED_ADULT_SURVIVAL_COLUMNS = {
    "temperature_c",
    "adult_age_days",
    "conditional_survival",
}


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Parameter file not found: {path}")

    frame = pd.read_csv(path)

    if frame.empty:
        raise ValueError(f"Parameter file is empty: {path}")

    return frame


def _require_columns(
    frame: pd.DataFrame,
    required: set[str],
    filename: str,
) -> None:
    missing = required.difference(frame.columns)

    if missing:
        raise ValueError(
            f"{filename} is missing required columns: "
            f"{sorted(missing)}"
        )


def load_parameter_registry(
    parameter_directory: str | Path,
    *,
    species: str,
    version: str,
    female_proportion: float,
    reproductive_lower_limit_c: float,
    reproductive_upper_limit_c: float,
    maximum_adult_age_days: int,
) -> BiologicalParameterRegistry:
    """
    Load biological parameter CSV files into one validated registry.
    """

    parameter_directory = Path(parameter_directory)

    thermal = _read_csv(
        parameter_directory / "thermal_development.csv"
    )

    fecundity = _read_csv(
        parameter_directory / "fecundity.csv"
    )

    adult_survival = _read_csv(
        parameter_directory / "adult_survival.csv"
    )

    _require_columns(
        thermal,
        REQUIRED_THERMAL_COLUMNS,
        "thermal_development.csv",
    )

    _require_columns(
        fecundity,
        REQUIRED_FECUNDITY_COLUMNS,
        "fecundity.csv",
    )

    _require_columns(
        adult_survival,
        REQUIRED_ADULT_SURVIVAL_COLUMNS,
        "adult_survival.csv",
    )

    # ---------------------------------------------------------
    # Immature-stage thermal records
    # ---------------------------------------------------------

    stage_parameters: dict[
        str,
        dict[float, StageThermalRecord],
    ] = {}

    for row in thermal.itertuples(index=False):
        stage = str(row.stage)
        temperature = float(row.temperature_c)

        duration = (
            None
            if pd.isna(row.mean_duration_days)
            else float(row.mean_duration_days)
        )

        survival = (
            None
            if pd.isna(row.conditional_survival)
            else float(row.conditional_survival)
        )

        stage_parameters.setdefault(stage, {})[
            temperature
        ] = StageThermalRecord(
            mean_duration_days=duration,
            conditional_survival=survival,
        )

    # ---------------------------------------------------------
    # Adult survival
    # ---------------------------------------------------------

    adult_survival_by_temperature: dict[
        float,
        dict[int, float],
    ] = {}

    for row in adult_survival.itertuples(index=False):
        temperature = float(row.temperature_c)
        age = int(row.adult_age_days)
        survival = float(row.conditional_survival)

        if not 0.0 <= survival <= 1.0:
            raise ValueError(
                "Adult conditional survival must lie between 0 and 1."
            )

        adult_survival_by_temperature.setdefault(
            temperature,
            {},
        )[age] = survival

    # ---------------------------------------------------------
    # Fecundity
    # ---------------------------------------------------------

    fecundity_by_temperature: dict[
        float,
        dict[int, float],
    ] = {}

    for row in fecundity.itertuples(index=False):
        temperature = float(row.temperature_c)
        age = int(row.female_age_days)
        eggs = float(row.eggs_per_female_day)

        if eggs < 0:
            raise ValueError(
                "Egg production cannot be negative."
            )

        fecundity_by_temperature.setdefault(
            temperature,
            {},
        )[age] = eggs

    metadata = {
        "thermal_development": ParameterMetadata(
            name="thermal_development",
            source=ParameterSource.LABORATORY,
            status=ParameterStatus.MEASURED_LOCKED,
        ),
        "immature_survival": ParameterMetadata(
            name="immature_survival",
            source=ParameterSource.LABORATORY,
            status=ParameterStatus.MEASURED_LOCKED,
        ),
        "adult_survival": ParameterMetadata(
            name="adult_survival",
            source=ParameterSource.LABORATORY,
            status=ParameterStatus.MEASURED_LOCKED,
        ),
        "fecundity": ParameterMetadata(
            name="fecundity",
            source=ParameterSource.LABORATORY,
            status=ParameterStatus.MEASURED_LOCKED,
        ),
    }

    return BiologicalParameterRegistry(
        species=species,
        version=version,
        stage_parameters=stage_parameters,
        adult_female_survival_by_age=(
            adult_survival_by_temperature
        ),
        fecundity_eggs_per_female_day=(
            fecundity_by_temperature
        ),
        female_proportion=female_proportion,
        reproductive_lower_limit_c=(
            reproductive_lower_limit_c
        ),
        reproductive_upper_limit_c=(
            reproductive_upper_limit_c
        ),
        maximum_adult_age_days=(
            maximum_adult_age_days
        ),
        metadata=metadata,
    )