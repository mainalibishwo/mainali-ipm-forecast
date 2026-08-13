"""
run_simulation.py

Run the APDM population engine through a sequence of daily weather records
using the biological parameters stored in data/parameters.
"""

from __future__ import annotations

import csv
from pathlib import Path

from backend.engine.parameter_manager import ParameterManager
from backend.engine.simulation import SimulationState
from backend.engine.weather_loader import WeatherLoader


PARAMETER_DIR = Path("data/parameters")
WEATHER_FILE = Path("data/weather/sample_weather.csv")
OUTPUT_FILE = Path("data/output/daily_population.csv")


def run_simulation(
    weather_file: str | Path = WEATHER_FILE,
    output_file: str | Path = OUTPUT_FILE,
    initial_eggs: float = 100.0,
) -> list[dict]:
    """Run a complete weather-driven population simulation."""

    weather_file = Path(weather_file)
    output_file = Path(output_file)

    # ---------------------------------------------------------
    # 1. Load biological parameters and construct engine
    # ---------------------------------------------------------

    manager = ParameterManager(PARAMETER_DIR).load()
    engine = manager.build_engine()

    # ---------------------------------------------------------
    # 2. Load weather
    # ---------------------------------------------------------

    weather = WeatherLoader.load_csv(weather_file)

    if not weather:
        raise ValueError("Weather file contains no records.")

    # ---------------------------------------------------------
    # 3. Initial population
    # ---------------------------------------------------------

    state = SimulationState(
        simulation_date=weather[0].weather_date,
        immature={
            "Egg": float(initial_eggs),
            "N1": 0.0,
            "N2": 0.0,
            "N3": 0.0,
            "N4": 0.0,
            "N5": 0.0,
        },
        adult_female_by_age={
            0: 0.0,
        },
        adult_male_by_age={
            0: 0.0,
        },
        cumulative_degree_days=0.0,
    )

    rows: list[dict] = []

    # ---------------------------------------------------------
    # 4. Daily simulation
    # ---------------------------------------------------------

    for weather_day in weather:

        result = engine.step(
            state,
            weather_day,
        )

        state = result.state

        rows.append(
            {
                "date": weather_day.weather_date.isoformat(),
                "tmin_c": weather_day.tmin,
                "tmax_c": weather_day.tmax,
                "tmean_c": weather_day.mean_temperature,
                "rainfall_mm": weather_day.rainfall_mm,

                "Egg": state.immature.get("Egg", 0.0),
                "N1": state.immature.get("N1", 0.0),
                "N2": state.immature.get("N2", 0.0),
                "N3": state.immature.get("N3", 0.0),
                "N4": state.immature.get("N4", 0.0),
                "N5": state.immature.get("N5", 0.0),

                "adult_females": state.adult_females,
                "adult_males": state.adult_males,

                "eggs_produced": result.eggs_produced,
                "potential_eggs": result.potential_eggs,
                "reproductive_activation": (
                    result.reproductive_activation
                ),
                "newly_emerged_adults": (
                    result.newly_emerged_adults
                ),
                "newly_emerged_females": (
                    result.newly_emerged_females
                ),
                "newly_emerged_males": (
                    result.newly_emerged_males
                ),

                "cumulative_degree_days": (
                    state.cumulative_degree_days
                ),

                "total_population": state.total_population,
            }
        )

    # ---------------------------------------------------------
    # 5. Export results
    # ---------------------------------------------------------

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_file.open(
        "w",
        newline="",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=list(rows[0].keys()),
        )

        writer.writeheader()
        writer.writerows(rows)

    return rows


if __name__ == "__main__":

    results = run_simulation()

    print(
        f"Simulation complete: {len(results)} days"
    )

    print(
        f"Output written to: {OUTPUT_FILE}"
    )

    print(
        f"Final population: "
        f"{results[-1]['total_population']:.3f}"
    )
