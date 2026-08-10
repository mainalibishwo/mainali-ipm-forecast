"""
simulation.py

Daily biological simulation engine for the Mainali IPM Forecast Engine (MIFE).

This module connects:
- weather
- thermal development
- immature survival
- stage progression
- adult ageing
- sex allocation
- reproduction

into a single deterministic daily timestep.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Mapping

from backend.engine.adult import AdultSurvivalModel
from backend.engine.development import DevelopmentModel
from backend.engine.fecundity import FecundityModel
from backend.engine.survival import SurvivalModel
from backend.engine.thermal import ThermalDevelopmentModel
from backend.engine.weather import WeatherDay


IMMATURE_STAGES: tuple[str, ...] = (
    "Egg",
    "N1",
    "N2",
    "N3",
    "N4",
    "N5",
)


@dataclass(frozen=True)
class SimulationState:
    """
    Internal daily state used by the biological engine.
    """

    simulation_date: date

    immature: Mapping[str, float]

    adult_female_by_age: Mapping[int, float]
    adult_male_by_age: Mapping[int, float]

    cumulative_degree_days: float = 0.0

    @property
    def adult_females(self) -> float:
        return sum(self.adult_female_by_age.values())

    @property
    def adult_males(self) -> float:
        return sum(self.adult_male_by_age.values())

    @property
    def total_population(self) -> float:
        return (
            sum(self.immature.values())
            + self.adult_females
            + self.adult_males
        )


@dataclass(frozen=True)
class DailySimulationResult:
    """
    Result of one biological timestep.
    """

    state: SimulationState

    eggs_produced: float

    newly_emerged_adults: float

    newly_emerged_females: float
    newly_emerged_males: float


class PopulationSimulationEngine:
    """
    Deterministic one-day Amblypelta population engine.
    """

    def __init__(
        self,
        thermal_model: ThermalDevelopmentModel,
        survival_model: SurvivalModel,
        adult_survival_model: AdultSurvivalModel,
        fecundity_model: FecundityModel,
        immature_stage_survival: Mapping[
            str,
            Mapping[float, float],
        ],
        female_proportion: float,
    ) -> None:

        if not 0.0 < female_proportion < 1.0:
            raise ValueError(
                "female_proportion must lie between 0 and 1."
            )

        self.thermal_model = thermal_model
        self.survival_model = survival_model
        self.adult_survival_model = adult_survival_model
        self.fecundity_model = fecundity_model

        self.immature_stage_survival = {
            stage: {
                float(temp): float(value)
                for temp, value in by_temperature.items()
            }
            for stage, by_temperature in immature_stage_survival.items()
        }

        self.female_proportion = female_proportion

    @staticmethod
    def _interpolate_survival(
        values: Mapping[float, float],
        temperature_c: float,
    ) -> float:

        points = sorted(
            (float(t), float(v))
            for t, v in values.items()
        )

        if not points:
            raise ValueError(
                "No survival observations supplied."
            )

        if temperature_c <= points[0][0]:
            return points[0][1]

        if temperature_c >= points[-1][0]:
            return points[-1][1]

        for (t0, v0), (t1, v1) in zip(
            points,
            points[1:],
        ):
            if t0 <= temperature_c <= t1:
                q = (
                    (temperature_c - t0)
                    / (t1 - t0)
                )

                return v0 + q * (v1 - v0)

        return points[-1][1]

    def step(
        self,
        state: SimulationState,
        weather: WeatherDay,
    ) -> DailySimulationResult:
        """
        Advance the population by exactly one day.
        """

        temperature = weather.mean_temperature

        next_immature = {
            stage: 0.0
            for stage in IMMATURE_STAGES
        }

        newly_emerged_adults = 0.0

        # -----------------------------------------------------
        # 1. Immature development + survival
        # -----------------------------------------------------

        incoming = 0.0

        for stage in IMMATURE_STAGES:

            abundance = (
                float(state.immature.get(stage, 0.0))
                + incoming
            )

            if abundance < 0:
                raise ValueError(
                    f"Negative abundance in {stage}."
                )

            duration = (
                self.thermal_model.mean_duration_days(
                    stage,
                    temperature,
                )
            )

            development_rate = (
                self.thermal_model.daily_development_rate(
                    stage,
                    temperature,
                )
            )

            whole_stage_survival = (
                self._interpolate_survival(
                    self.immature_stage_survival[stage],
                    temperature,
                )
            )

            daily_survival = (
                self.survival_model.daily_survival_probability(
                    whole_stage_survival,
                    duration,
                )
            )

            surviving = (
                self.survival_model.survivors(
                    abundance,
                    daily_survival,
                )
            )

            transition = (
                DevelopmentModel.transition(
                    surviving,
                    development_rate,
                )
            )

            next_immature[stage] += (
                transition.remaining
            )

            if stage == "N5":
                newly_emerged_adults += (
                    transition.progressed
                )

                incoming = 0.0
            else:
                incoming = transition.progressed

        # -----------------------------------------------------
        # 2. Adult ageing + survival
        # -----------------------------------------------------

        next_females = (
            self.adult_survival_model.age_one_day(
                state.adult_female_by_age,
                temperature,
            )
        )

        next_males = (
            self.adult_survival_model.age_one_day(
                state.adult_male_by_age,
                temperature,
            )
        )

        # -----------------------------------------------------
        # 3. Add newly emerged adults
        # -----------------------------------------------------

        newly_emerged_females = (
            newly_emerged_adults
            * self.female_proportion
        )

        newly_emerged_males = (
            newly_emerged_adults
            * (1.0 - self.female_proportion)
        )

        next_females[0] = (
            next_females.get(0, 0.0)
            + newly_emerged_females
        )

        next_males[0] = (
            next_males.get(0, 0.0)
            + newly_emerged_males
        )

        # -----------------------------------------------------
        # 4. Reproduction
        # -----------------------------------------------------

        eggs_produced = (
            self.fecundity_model.daily_egg_production(
                next_females,
                temperature,
            )
        )

        next_immature["Egg"] += eggs_produced

        # -----------------------------------------------------
        # 5. Approximate thermal accumulation
        # -----------------------------------------------------

        degree_day_increment = max(
            0.0,
            temperature
            - self.fecundity_model.lower_limit,
        )

        next_state = SimulationState(
            simulation_date=weather.weather_date,
            immature=next_immature,
            adult_female_by_age=next_females,
            adult_male_by_age=next_males,
            cumulative_degree_days=(
                state.cumulative_degree_days
                + degree_day_increment
            ),
        )

        return DailySimulationResult(
            state=next_state,
            eggs_produced=eggs_produced,
            newly_emerged_adults=newly_emerged_adults,
            newly_emerged_females=newly_emerged_females,
            newly_emerged_males=newly_emerged_males,
        )