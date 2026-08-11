"""
api.py

API layer for the Mainali APDM forecasting system.

Connects the population simulation engine to the web interface.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
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
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PARAMETER_DIR = Path("data/parameters")


class SimulationRequest(BaseModel):
    """Input supplied by the forecasting interface."""

    weather_file: str
    initial_eggs: float = Field(
        default=100.0,
        ge=0,
    )


@app.get("/")
def root():
    return FileResponse("frontend/index.html")


@app.get("/health")
def health():
    return {
        "status": "ok",
    }


@app.post("/simulate")
def simulate(request: SimulationRequest):

    weather_path = Path(request.weather_file)

    if not weather_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Weather file not found: {weather_path}",
        )

    try:
        # Load scientific parameters
        manager = ParameterManager(
            PARAMETER_DIR
        ).load()

        engine = manager.build_engine()

        # Load daily weather
        weather = WeatherLoader.load_csv(
            weather_path
        )

        if not weather:
            raise ValueError(
                "Weather file contains no records."
            )

        # Initial population state
        state = SimulationState(
            simulation_date=weather[0].weather_date,
            immature={
                "Egg": float(request.initial_eggs),
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

        daily_results = []

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
                    "tmin": weather_day.tmin,
                    "tmax": weather_day.tmax,
                    "rainfall_mm": (
                        weather_day.rainfall_mm
                    ),
                    "egg": (
                        state.immature.get(
                            "Egg",
                            0.0,
                        )
                    ),
                    "n1": state.immature.get(
                        "N1",
                        0.0,
                    ),
                    "n2": state.immature.get(
                        "N2",
                        0.0,
                    ),
                    "n3": state.immature.get(
                        "N3",
                        0.0,
                    ),
                    "n4": state.immature.get(
                        "N4",
                        0.0,
                    ),
                    "n5": state.immature.get(
                        "N5",
                        0.0,
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
                    "degree_days": (
                        state
                        .cumulative_degree_days
                    ),
                    "total_population": (
                        state.total_population
                    ),
                }
            )

        return {
            "model": (
                "Amblypelta Population "
                "Dynamics Model"
            ),
            "days_simulated": len(
                daily_results
            ),
            "initial_eggs": (
                request.initial_eggs
            ),
            "final_population": (
                state.total_population
            ),
            "results": daily_results,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc