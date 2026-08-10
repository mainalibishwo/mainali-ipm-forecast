"""
parameter_manager.py

Loads biological parameter CSV files and constructs all models required by the
PopulationSimulationEngine.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from backend.engine.adult import AdultSurvivalModel
from backend.engine.fecundity import FecundityModel
from backend.engine.simulation import PopulationSimulationEngine
from backend.engine.survival import SurvivalModel
from backend.engine.thermal import ThermalDevelopmentModel


IMMATURE_STAGES = ("Egg", "N1", "N2", "N3", "N4", "N5")


class ParameterManager:
    """Load biological parameter files and build a configured engine."""

    def __init__(self, parameter_directory: str | Path):
        self.parameter_directory = Path(parameter_directory)

        self.thermal = None
        self.fecundity = None
        self.adult = None

        self.immature_stage_survival = None

    def load(self):
        thermal_path = (
            self.parameter_directory
            / "thermal_development.csv"
        )

        fecundity_path = (
            self.parameter_directory
            / "fecundity.csv"
        )

        adult_path = (
            self.parameter_directory
            / "adult_survival.csv"
        )

        for path in (
            thermal_path,
            fecundity_path,
            adult_path,
        ):
            if not path.exists():
                raise FileNotFoundError(path)

        thermal_df = pd.read_csv(thermal_path)
        fecundity_df = pd.read_csv(fecundity_path)
        adult_df = pd.read_csv(adult_path)

        # -------------------------------------------------
        # Thermal development + immature survival
        # -------------------------------------------------

        thermal_mapping = {}
        immature_survival = {}

        for stage in IMMATURE_STAGES:
            thermal_mapping[stage] = {}
            immature_survival[stage] = {}

        for row in thermal_df.itertuples(index=False):
            stage = str(row.stage)
            temperature = float(row.temperature_c)

            if stage not in IMMATURE_STAGES:
                raise ValueError(
                    f"Unknown immature stage: {stage}"
                )

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

            thermal_mapping[stage][str(temperature)] = {
                "mean_duration_days": duration,
                "conditional_survival": survival,
            }

            if survival is not None:
                immature_survival[stage][temperature] = survival

        self.thermal = ThermalDevelopmentModel(
            thermal_mapping
        )

        self.immature_stage_survival = (
            immature_survival
        )

        # -------------------------------------------------
        # Fecundity
        # -------------------------------------------------

        fecundity_mapping = {}

        for row in fecundity_df.itertuples(index=False):
            temperature = float(row.temperature_c)
            age = int(row.female_age_days)
            eggs = float(row.eggs_per_female_day)

            if eggs < 0:
                raise ValueError(
                    "Fecundity cannot be negative."
                )

            fecundity_mapping.setdefault(
                temperature,
                {},
            )[age] = eggs

        self.fecundity = FecundityModel(
            fecundity_by_temperature=fecundity_mapping,
            reproductive_lower_limit_c=15.0,
            reproductive_upper_limit_c=35.0,
            maximum_adult_age_days=160,
        )

        # -------------------------------------------------
        # Adult survival
        # -------------------------------------------------

        adult_mapping = {}

        for row in adult_df.itertuples(index=False):
            temperature = float(row.temperature_c)
            age = int(row.adult_age_days)
            survival = float(row.conditional_survival)

            if not 0.0 <= survival <= 1.0:
                raise ValueError(
                    "Adult survival must lie between 0 and 1."
                )

            adult_mapping.setdefault(
                temperature,
                {},
            )[age] = survival

        self.adult = AdultSurvivalModel(
            survival_by_temperature=adult_mapping,
            maximum_age_days=160,
        )

        return self

    def build_engine(self):
        if (
            self.thermal is None
            or self.fecundity is None
            or self.adult is None
            or self.immature_stage_survival is None
        ):
            raise RuntimeError(
                "Call load() before build_engine()."
            )

        return PopulationSimulationEngine(
            thermal_model=self.thermal,
            survival_model=SurvivalModel(),
            adult_survival_model=self.adult,
            fecundity_model=self.fecundity,
            immature_stage_survival=(
                self.immature_stage_survival
            ),
            female_proportion=0.5,
        )