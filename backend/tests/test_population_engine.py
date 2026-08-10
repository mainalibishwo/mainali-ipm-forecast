from datetime import date, timedelta

from backend.engine.adult import AdultSurvivalModel
from backend.engine.fecundity import FecundityModel
from backend.engine.simulation import (
    PopulationSimulationEngine,
    SimulationState,
)
from backend.engine.survival import SurvivalModel
from backend.engine.thermal import ThermalDevelopmentModel
from backend.engine.weather import WeatherDay


def build_test_engine():
    stage_parameters = {}

    for stage in ("Egg", "N1", "N2", "N3", "N4", "N5"):
        stage_parameters[stage] = {
            "20": {
                "mean_duration_days": 5.0,
                "conditional_survival": 0.95,
            },
            "25": {
                "mean_duration_days": 4.0,
                "conditional_survival": 0.95,
            },
        }

    thermal = ThermalDevelopmentModel(stage_parameters)

    adult = AdultSurvivalModel(
        survival_by_temperature={
            20: {
                age: 0.98
                for age in range(0, 31)
            },
            25: {
                age: 0.97
                for age in range(0, 31)
            },
        },
        maximum_age_days=30,
    )

    fecundity = FecundityModel(
        fecundity_by_temperature={
            20: {
                age: (0.0 if age < 3 else 2.0)
                for age in range(0, 31)
            },
            25: {
                age: (0.0 if age < 3 else 3.0)
                for age in range(0, 31)
            },
        },
        reproductive_lower_limit_c=15,
        reproductive_upper_limit_c=35,
        maximum_adult_age_days=30,
    )

    immature_survival = {
        stage: {
            20: 0.95,
            25: 0.95,
        }
        for stage in ("Egg", "N1", "N2", "N3", "N4", "N5")
    }

    return PopulationSimulationEngine(
        thermal_model=thermal,
        survival_model=SurvivalModel(),
        adult_survival_model=adult,
        fecundity_model=fecundity,
        immature_stage_survival=immature_survival,
        female_proportion=0.5,
    )


def test_population_engine_runs_multiple_days():
    engine = build_test_engine()

    start_date = date(2026, 8, 10)

    state = SimulationState(
        simulation_date=start_date,
        immature={
            "Egg": 100.0,
            "N1": 0.0,
            "N2": 0.0,
            "N3": 0.0,
            "N4": 0.0,
            "N5": 0.0,
        },
        adult_female_by_age={0: 0.0},
        adult_male_by_age={0: 0.0},
    )

    results = []

    for day in range(40):
        weather = WeatherDay(
            weather_date=start_date + timedelta(days=day + 1),
            tmin=18.0,
            tmax=26.0,
            rainfall_mm=0.0,
        )

        result = engine.step(
            state,
            weather,
        )

        state = result.state
        results.append(result)

        assert state.total_population >= 0.0

        assert all(
            value >= 0.0
            for value in state.immature.values()
        )

        assert all(
            value >= 0.0
            for value in state.adult_female_by_age.values()
        )

        assert all(
            value >= 0.0
            for value in state.adult_male_by_age.values()
        )

    assert len(results) == 40

    assert any(
        result.newly_emerged_adults > 0.0
        for result in results
    )

    assert any(
        result.eggs_produced > 0.0
        for result in results
    )

    assert state.cumulative_degree_days > 0.0


def test_sex_allocation_is_conservative():
    engine = build_test_engine()

    state = SimulationState(
        simulation_date=date(2026, 8, 10),
        immature={
            "Egg": 0.0,
            "N1": 0.0,
            "N2": 0.0,
            "N3": 0.0,
            "N4": 0.0,
            "N5": 100.0,
        },
        adult_female_by_age={0: 0.0},
        adult_male_by_age={0: 0.0},
    )

    weather = WeatherDay(
        weather_date=date(2026, 8, 11),
        tmin=20.0,
        tmax=24.0,
    )

    result = engine.step(
        state,
        weather,
    )

    assert abs(
        (
            result.newly_emerged_females
            + result.newly_emerged_males
        )
        - result.newly_emerged_adults
    ) < 1e-10