"""
run_simulation.py

Runs a complete weather-driven simulation and exports daily results.
"""

from __future__ import annotations

import csv
from datetime import date

from backend.engine.simulation import (
    PopulationSimulationEngine,
    SimulationState,
)
from backend.engine.weather_loader import WeatherLoader


def run_simulation(
    engine: PopulationSimulationEngine,
    weather_csv: str,
    output_csv: str,
):
    """
    Run the simulation through every day in the weather file.
    """

    weather = WeatherLoader.load_csv(weather_csv)

    state = SimulationState(
        simulation_date=weather[0].weather_date,
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

    rows = []

    for day in weather:

        result = engine.step(
            state,
            day,
        )

        state = result.state

        rows.append(
            {
                "date": state.simulation_date.isoformat(),
                "Egg": state.immature["Egg"],
                "N1": state.immature["N1"],
                "N2": state.immature["N2"],
                "N3": state.immature["N3"],
                "N4": state.immature["N4"],
                "N5": state.immature["N5"],
                "Adult females": sum(
                    state.adult_female_by_age.values()
                ),
                "Adult males": sum(
                    state.adult_male_by_age.values()
                ),
                "Total population": state.total_population,
            }
        )

    with open(
        output_csv,
        "w",
        newline="",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=rows[0].keys(),
        )

        writer.writeheader()
        writer.writerows(rows)

    print(
        f"Simulation complete. "
        f"{len(rows)} days exported to {output_csv}"
    )