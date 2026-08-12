"""
simulation.py

Daily biological simulation engine for the Mainali IPM Forecast Engine (MIFE).

This module connects:
- weather
- thermal development
- immature survival
- physiological stage progression
- adult ageing
- sex allocation
- reproduction

into a single deterministic daily timestep.

Immature development is represented using physiological progress.

Each immature cohort carries:
    abundance
    progress through its current stage

Progress is expressed from 0.0 to <1.0.

For each day:
    progress += daily development rate

A cohort moves to the next stage only when accumulated progress reaches
or exceeds 1.0.

Individuals entering a new stage are not processed again until the next
daily timestep. This prevents biologically impossible same-day cascading
through multiple immature stages.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Mapping

from backend.engine.adult import AdultSurvivalModel
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


Cohort = tuple[float, float]
# Cohort = (abundance, physiological_progress)


@dataclass(frozen=True)
class SimulationState:
    """
    Internal daily state used by the biological engine.

    immature
        Aggregate abundance in each immature stage. This field is
        retained for API compatibility and reporting.

    immature_cohorts
        Internal physiological-age representation. Each stage maps
        to a tuple of (abundance, progress) cohorts.

        Existing code that constructs SimulationState without this
        field remains valid. In that case each non-zero aggregate
        immature stage is initialised as one cohort at progress 0.
    """

    simulation_date: date

    immature: Mapping[str, float]

    adult_female_by_age: Mapping[int, float]
    adult_male_by_age: Mapping[int, float]

    cumulative_degree_days: float = 0.0

    immature_cohorts: Mapping[
        str,
        tuple[Cohort, ...],
    ] = field(default_factory=dict)

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
            for stage, by_temperature
            in immature_stage_survival.items()
        }

        self.female_proportion = float(
            female_proportion
        )

    @staticmethod
    def _interpolate_survival(
        values: Mapping[float, float],
        temperature_c: float,
    ) -> float:
        """
        Return whole-stage survival at the requested temperature.

        Linear interpolation is used between measured temperatures.

        Outside the measured temperature range for a stage, the
        nearest available observation is retained. This is explicit
        boundary clamping rather than evidence that survival was
        measured at the extrapolated temperature.

        Biological failure at extreme temperatures is still captured
        where a measured boundary value is zero, for example egg
        survival at 35 C.
        """

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

                return (
                    v0
                    + q * (v1 - v0)
                )

        return points[-1][1]

    @staticmethod
    def _initialise_cohorts(
        state: SimulationState,
    ) -> dict[str, list[Cohort]]:
        """
        Return mutable immature cohorts for today's timestep.

        If physiological-age cohorts already exist, they are used.

        Otherwise aggregate stage abundance is converted into one
        progress-zero cohort for each occupied stage. This maintains
        compatibility with existing initial-state construction.
        """

        cohorts: dict[str, list[Cohort]] = {
            stage: []
            for stage in IMMATURE_STAGES
        }

        has_cohort_state = any(
            state.immature_cohorts.get(stage)
            for stage in IMMATURE_STAGES
        )

        if has_cohort_state:

            for stage in IMMATURE_STAGES:

                for abundance, progress in (
                    state.immature_cohorts.get(
                        stage,
                        (),
                    )
                ):

                    abundance = float(abundance)
                    progress = float(progress)

                    if abundance < 0:
                        raise ValueError(
                            f"Negative abundance in "
                            f"{stage} cohort."
                        )

                    if not 0.0 <= progress < 1.0:
                        raise ValueError(
                            f"Invalid physiological progress "
                            f"in {stage}: {progress}."
                        )

                    if abundance > 0:
                        cohorts[stage].append(
                            (
                                abundance,
                                progress,
                            )
                        )

            return cohorts

        for stage in IMMATURE_STAGES:

            abundance = float(
                state.immature.get(
                    stage,
                    0.0,
                )
            )

            if abundance < 0:
                raise ValueError(
                    f"Negative abundance in {stage}."
                )

            if abundance > 0:

                cohorts[stage].append(
                    (
                        abundance,
                        0.0,
                    )
                )

        return cohorts

    @staticmethod
    def _aggregate_cohorts(
        cohorts: Mapping[
            str,
            list[Cohort],
        ],
    ) -> dict[str, float]:
        """
        Aggregate physiological cohorts into stage abundance.
        """

        return {
            stage: sum(
                abundance
                for abundance, _progress
                in cohorts.get(stage, [])
            )
            for stage in IMMATURE_STAGES
        }

    def step(
        self,
        state: SimulationState,
        weather: WeatherDay,
    ) -> DailySimulationResult:
        """
        Advance the population by exactly one day.
        """

        temperature = (
            weather.mean_temperature
        )

        current_cohorts = (
            self._initialise_cohorts(
                state
            )
        )

        next_cohorts: dict[
            str,
            list[Cohort],
        ] = {
            stage: []
            for stage in IMMATURE_STAGES
        }

        progressed_to_next: dict[
            str,
            float,
        ] = {
            stage: 0.0
            for stage in IMMATURE_STAGES
        }

        newly_emerged_adults = 0.0

        # -----------------------------------------------------
        # 1. Immature physiological development + survival
        # -----------------------------------------------------

        for stage in IMMATURE_STAGES:

            duration = (
                self.thermal_model.mean_duration_days(
                    stage,
                    temperature,
                )
            )

            if duration <= 0:
                raise ValueError(
                    f"Non-positive development "
                    f"duration for {stage}."
                )

            development_rate = (
                self.thermal_model.daily_development_rate(
                    stage,
                    temperature,
                )
            )

            if development_rate < 0:
                raise ValueError(
                    f"Negative development rate "
                    f"for {stage}."
                )

            whole_stage_survival = (
                self._interpolate_survival(
                    self.immature_stage_survival[
                        stage
                    ],
                    temperature,
                )
            )

            daily_survival = (
                self.survival_model
                .daily_survival_probability(
                    whole_stage_survival,
                    duration,
                )
            )

            for (
                abundance,
                progress,
            ) in current_cohorts[stage]:

                surviving = (
                    self.survival_model.survivors(
                        abundance,
                        daily_survival,
                    )
                )

                if surviving <= 0:
                    continue

                new_progress = (
                    progress
                    + development_rate
                )

                if new_progress >= 1.0:

                    progressed_to_next[
                        stage
                    ] += surviving

                else:

                    next_cohorts[
                        stage
                    ].append(
                        (
                            surviving,
                            new_progress,
                        )
                    )

        # -----------------------------------------------------
        # 2. Move completed cohorts forward one stage
        # -----------------------------------------------------
        #
        # Movement occurs only after every beginning-of-day
        # immature cohort has been processed.
        #
        # Therefore a cohort can move at most one immature stage
        # during one daily timestep.

        for index, stage in enumerate(
            IMMATURE_STAGES
        ):

            progressed = (
                progressed_to_next[
                    stage
                ]
            )

            if progressed <= 0:
                continue

            if stage == "N5":

                newly_emerged_adults += (
                    progressed
                )

            else:

                next_stage = (
                    IMMATURE_STAGES[
                        index + 1
                    ]
                )

                next_cohorts[
                    next_stage
                ].append(
                    (
                        progressed,
                        0.0,
                    )
                )

        # -----------------------------------------------------
        # 3. Adult ageing + survival
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
        # 4. Reproduction by females already present
        # -----------------------------------------------------
        #
        # Newly emerged females are deliberately added only after
        # reproduction has been calculated. They therefore cannot
        # reproduce on their day of adult emergence.

        eggs_produced = (
            self.fecundity_model.daily_egg_production(
                next_females,
                temperature,
            )
        )

        if eggs_produced < 0:
            raise ValueError(
                "Egg production cannot be negative."
            )

        if eggs_produced > 0:

            next_cohorts[
                "Egg"
            ].append(
                (
                    eggs_produced,
                    0.0,
                )
            )

        # -----------------------------------------------------
        # 5. Add newly emerged adults
        # -----------------------------------------------------

        newly_emerged_females = (
            newly_emerged_adults
            * self.female_proportion
        )

        newly_emerged_males = (
            newly_emerged_adults
            * (
                1.0
                - self.female_proportion
            )
        )

        next_females[0] = (
            next_females.get(
                0,
                0.0,
            )
            + newly_emerged_females
        )

        next_males[0] = (
            next_males.get(
                0,
                0.0,
            )
            + newly_emerged_males
        )

        # -----------------------------------------------------
        # 6. Aggregate immature stage abundance for reporting
        # -----------------------------------------------------

        next_immature = (
            self._aggregate_cohorts(
                next_cohorts
            )
        )

        # -----------------------------------------------------
        # 7. Approximate thermal accumulation
        # -----------------------------------------------------
        #
        # Retained for compatibility with current diagnostics.
        # This is not used to control stage progression.

        degree_day_increment = max(
            0.0,
            temperature
            - self.fecundity_model.lower_limit,
        )

        frozen_cohorts = {
            stage: tuple(
                next_cohorts[stage]
            )
            for stage in IMMATURE_STAGES
        }

        next_state = SimulationState(
            simulation_date=weather.weather_date,
            immature=next_immature,
            adult_female_by_age=next_females,
            adult_male_by_age=next_males,
            cumulative_degree_days=(
                state.cumulative_degree_days
                + degree_day_increment
            ),
            immature_cohorts=frozen_cohorts,
        )

        return DailySimulationResult(
            state=next_state,
            eggs_produced=eggs_produced,
            newly_emerged_adults=(
                newly_emerged_adults
            ),
            newly_emerged_females=(
                newly_emerged_females
            ),
            newly_emerged_males=(
                newly_emerged_males
            ),
        )
