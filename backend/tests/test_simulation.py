from datetime import date

from backend.engine.weather import WeatherDay
from backend.engine.thermal import ThermalDevelopmentModel
from backend.engine.development import DevelopmentModel
from backend.engine.survival import SurvivalModel
from backend.engine.fecundity import FecundityModel
from backend.engine.adult import AdultSurvivalModel


def test_engine_components_integrate():

    weather = WeatherDay(
        weather_date=date(2026, 8, 10),
        tmin=15,
        tmax=28,
        rainfall_mm=2,
    )

    assert weather.mean_temperature == 21.5

    # Minimal toy thermal dataset for software testing only.
    thermal = ThermalDevelopmentModel(
        {
            "Egg": {
                "20": {
                    "mean_duration_days": 10.0,
                    "conditional_survival": 0.90,
                },
                "25": {
                    "mean_duration_days": 5.0,
                    "conditional_survival": 0.95,
                },
            }
        }
    )

    duration = thermal.mean_duration_days("Egg", 22.5)

    assert duration > 0

    development_rate = thermal.daily_development_rate(
        "Egg",
        22.5,
    )

    assert development_rate > 0

    transition = DevelopmentModel.transition(
        population=100,
        daily_development_rate=0.20,
    )

    assert transition.remaining == 80.0
    assert transition.progressed == 20.0

    daily_survival = SurvivalModel.daily_survival_probability(
        conditional_survival=0.90,
        stage_duration_days=10.0,
    )

    assert 0.0 < daily_survival <= 1.0

    survivors = SurvivalModel.survivors(
        population=100,
        daily_survival_probability=daily_survival,
    )

    assert 0.0 < survivors <= 100.0

    fecundity = FecundityModel(
        fecundity_by_temperature={
            20: {5: 1.0},
            25: {5: 3.0},
            30: {5: 2.0},
        },
        reproductive_lower_limit_c=15,
        reproductive_upper_limit_c=35,
        maximum_adult_age_days=100,
    )

    assert fecundity.eggs_per_female_day(25, 5) == 3.0

    adults = AdultSurvivalModel(
        survival_by_temperature={
            25: {
                0: 0.95,
                1: 0.90,
            },
            30: {
                0: 0.90,
                1: 0.85,
            },
        },
        maximum_age_days=100,
    )

    assert adults.conditional_survival(25, 0) == 0.95