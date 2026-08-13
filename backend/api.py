"""
api.py

API layer for the Mainali APDM forecasting system.

Connects the population simulation engine to the web interface.
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend.engine.parameter_manager import ParameterManager
from backend.engine.simulation import SimulationState
from backend.engine.weather_loader import WeatherLoader


app = FastAPI(
    title="Mainali APDM Forecast API",
    description=(
        "Weather-driven Amblypelta population dynamics "
        "decision-support API."
    ),
    version="1.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


PARAMETER_DIR = Path("data/parameters")
WEATHER_DIR = Path("data/weather")


LOCATIONS = {
    "demo": {
        "name": "Demonstration weather",
        "region": "Demonstration",
        "weather_file": "sample_weather.csv",
    },

    # Existing Northern NSW test series
    "malua": {
        "name": "Northern NSW — Malua test series",
        "region": "Northern NSW",
        "weather_file": "nnsw_malua_2025_2026.csv",
    },
    "knockrow": {
        "name": "Northern NSW — Knockrow test series",
        "region": "Northern NSW",
        "weather_file": "nnsw_knockrow_2025_2026.csv",
    },
    "dorey": {
        "name": "Northern NSW — Dorey test series",
        "region": "Northern NSW",
        "weather_file": "nnsw_dorey_2025_2026.csv",
    },

    # Historical de-identified regional weather series
    "western_downs_01": {
        "name": "Western Downs — Site 1",
        "region": "Western Downs",
        "weather_file": "western_downs_01.csv",
    },
    "wide_bay_gympie_01": {
        "name": "Wide Bay–Gympie — Site 1",
        "region": "Wide Bay–Gympie",
        "weather_file": "wide_bay_gympie_01.csv",
    },
    "wide_bay_gympie_02": {
        "name": "Wide Bay–Gympie — Site 2",
        "region": "Wide Bay–Gympie",
        "weather_file": "wide_bay_gympie_02.csv",
    },
    "glass_house_mountains_01": {
        "name": "Glass House Mountains — Site 1",
        "region": "Glass House Mountains",
        "weather_file": "glass_house_mountains_01.csv",
    },
    "bundaberg_region_01": {
        "name": "Bundaberg Region — Site 1",
        "region": "Bundaberg Region",
        "weather_file": "bundaberg_region_01.csv",
    },
    "northern_nsw_01": {
        "name": "Northern NSW — Site 1",
        "region": "Northern NSW",
        "weather_file": "northern_nsw_01.csv",
    },
    "northern_nsw_02": {
        "name": "Northern NSW — Site 2",
        "region": "Northern NSW",
        "weather_file": "northern_nsw_02.csv",
    },
    "northern_nsw_03": {
        "name": "Northern NSW — Site 3",
        "region": "Northern NSW",
        "weather_file": "northern_nsw_03.csv",
    },
    "northern_nsw_04": {
        "name": "Northern NSW — Site 4",
        "region": "Northern NSW",
        "weather_file": "northern_nsw_04.csv",
    },
}

class SimulationRequest(BaseModel):
    """Input supplied by the forecasting interface."""

    location: str = "demo"

    initial_eggs: float = Field(
        default=100.0,
        ge=0,
    )

    initialization: Literal[
        "eggs",
        "overwintering_adults",
    ] = "eggs"

    initial_adult_females_by_age: dict[int, float] = Field(
        default_factory=dict,
    )

    initial_adult_males_by_age: dict[int, float] = Field(
        default_factory=dict,
    )

    start_date: str | None = None
    end_date: str | None = None


@app.get("/")
def root():
    return FileResponse(
        "frontend/index.html"
    )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model": (
            "Amblypelta Population "
            "Dynamics Model"
        ),
    }


@app.get("/locations")
def locations():
    """Return locations currently available to the interface."""

    return {
        "locations": [
            {
                "id": location_id,
                "name": values["name"],
                "region": values["region"],
            }
            for location_id, values
            in LOCATIONS.items()
        ]
    }


@app.post("/simulate")
def simulate(
    request: SimulationRequest,
):

    if request.location not in LOCATIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unknown location: "
                f"{request.location}"
            ),
        )

    location_info = (
        LOCATIONS[request.location]
    )

    weather_path = (
        WEATHER_DIR
        / location_info["weather_file"]
    )

    if not weather_path.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                f"Weather data not available "
                f"for {location_info['name']}: "
                f"{weather_path}"
            ),
        )

    try:

        # -----------------------------------------
        # Load biological parameters
        # -----------------------------------------

        manager = ParameterManager(
            PARAMETER_DIR
        ).load()

        engine = manager.build_engine()

             # -----------------------------------------
        # Load weather
        # -----------------------------------------

        weather = WeatherLoader.load_csv(
            weather_path
        )

        if request.start_date:
            start_date = datetime.strptime(
                request.start_date,
                "%Y-%m-%d",
            ).date()

            weather = [
                day for day in weather
                if day.weather_date >= start_date
            ]

        if request.end_date:
            end_date = datetime.strptime(
                request.end_date,
                "%Y-%m-%d",
            ).date()

            weather = [
                day for day in weather
                if day.weather_date <= end_date
            ]

        if not weather:
            raise ValueError(
                "Weather file contains no records."
            )

        # -----------------------------------------
        # Initial population
        # -----------------------------------------

        females_by_age = {
            int(age): float(abundance)
            for age, abundance
            in request.initial_adult_females_by_age.items()
        }
        males_by_age = {
            int(age): float(abundance)
            for age, abundance
            in request.initial_adult_males_by_age.items()
        }

        for label, distribution in (
            ("female", females_by_age),
            ("male", males_by_age),
        ):
            for age, abundance in distribution.items():
                if age < 0:
                    raise ValueError(
                        f"Initial {label} adult age cannot be negative."
                    )
                if age > engine.adult_survival_model.maximum_age_days:
                    raise ValueError(
                        f"Initial {label} adult age {age} exceeds "
                        "the frozen maximum adult age."
                    )
                if abundance < 0:
                    raise ValueError(
                        f"Initial {label} adult abundance cannot be negative."
                    )

        if request.initialization == "eggs":
            if females_by_age or males_by_age:
                raise ValueError(
                    "Adult age distributions require "
                    "initialization='overwintering_adults'."
                )
            initial_eggs = float(request.initial_eggs)
            females_by_age = {0: 0.0}
            males_by_age = {0: 0.0}
        else:
            if request.initial_eggs != 0:
                raise ValueError(
                    "Set initial_eggs=0 for overwintering-adult initialization."
                )
            if sum(females_by_age.values()) + sum(males_by_age.values()) <= 0:
                raise ValueError(
                    "Overwintering-adult initialization requires "
                    "a positive adult abundance."
                )
            initial_eggs = 0.0

        state = SimulationState(
            simulation_date=(
                weather[0].weather_date
            ),

            immature={
                "Egg": float(
                    initial_eggs
                ),
                "N1": 0.0,
                "N2": 0.0,
                "N3": 0.0,
                "N4": 0.0,
                "N5": 0.0,
            },

            adult_female_by_age=females_by_age,

            adult_male_by_age=males_by_age,

            cumulative_degree_days=0.0,
        )

        daily_results = []

        # -----------------------------------------
        # Run daily simulation
        # -----------------------------------------

        for weather_day in weather:

            result = engine.step(
                state,
                weather_day,
            )

            state = result.state

            daily_results.append(
                {
                    "date": (
                        weather_day
                        .weather_date
                        .isoformat()
                    ),

                    "tmin": (
                        weather_day.tmin
                    ),

                    "tmax": (
                        weather_day.tmax
                    ),

                    "tmean": (
                        weather_day
                        .mean_temperature
                    ),

                    "rainfall_mm": (
                        weather_day
                        .rainfall_mm
                    ),

                    "egg": (
                        state.immature.get(
                            "Egg",
                            0.0,
                        )
                    ),

                    "n1": (
                        state.immature.get(
                            "N1",
                            0.0,
                        )
                    ),

                    "n2": (
                        state.immature.get(
                            "N2",
                            0.0,
                        )
                    ),

                    "n3": (
                        state.immature.get(
                            "N3",
                            0.0,
                        )
                    ),

                    "n4": (
                        state.immature.get(
                            "N4",
                            0.0,
                        )
                    ),

                    "n5": (
                        state.immature.get(
                            "N5",
                            0.0,
                        )
                    ),

                    "adult_females": (
                        state.adult_females
                    ),

                    "adult_males": (
                        state.adult_males
                    ),

                    "new_adults": (
                        result
                        .newly_emerged_adults
                    ),

                    "eggs_produced": (
                        result.eggs_produced
                    ),

                    "potential_eggs": (
                        result.potential_eggs
                    ),

                    "reproductive_activation": (
                        result.reproductive_activation
                    ),

                    "degree_days": (
                        state
                        .cumulative_degree_days
                    ),

                    "total_population": (
                        state.total_population
                    ),
                }
            )

        peak_population = max(
            row["total_population"]
            for row in daily_results
        )

        peak_row = max(
            daily_results,
            key=lambda row:
                row["total_population"],
        )

        return {
            "model": (
                "Amblypelta Population "
                "Dynamics Model"
            ),

            "location_id": (
                request.location
            ),

            "location": (
                location_info["name"]
            ),

            "region": (
                location_info["region"]
            ),

            "start_date": (
                daily_results[0]["date"]
            ),

            "end_date": (
                daily_results[-1]["date"]
            ),

            "days_simulated": len(
                daily_results
            ),

            "initial_eggs": (
                initial_eggs
            ),

            "initialization": (
                request.initialization
            ),

            "initial_adult_females_by_age": (
                females_by_age
            ),

            "initial_adult_males_by_age": (
                males_by_age
            ),

            "final_population": (
                state.total_population
            ),

            "peak_population": (
                peak_population
            ),

            "peak_date": (
                peak_row["date"]
            ),

            "results": (
                daily_results
            ),
        }

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc
