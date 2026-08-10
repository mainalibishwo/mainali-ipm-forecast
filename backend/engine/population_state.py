"""
population_state.py

Core biological state representation for the Mainali IPM Forecast Engine (MIFE).

Each PopulationState represents the estimated biological state of one orchard
on one day. The object is immutable so that every simulation step is
reproducible and traceable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Dict


@dataclass(frozen=True)
class PopulationState:
    """
    Daily biological population state.

    All abundances represent estimated numbers within the simulated orchard.
    """

    # Simulation date
    simulation_date: date

    # Immature stages
    eggs: float = 0.0

    n1: float = 0.0
    n2: float = 0.0
    n3: float = 0.0
    n4: float = 0.0
    n5: float = 0.0

    # Adults
    adult_female: float = 0.0
    adult_male: float = 0.0

    # Model diagnostics
    generation: int = 1

    accumulated_degree_days: float = 0.0

    population_growth_rate: float = 1.0

    uncertainty: float = 0.0

    metadata: Dict[str, str] = field(default_factory=dict)

    @property
    def total_nymphs(self) -> float:
        return (
            self.n1 +
            self.n2 +
            self.n3 +
            self.n4 +
            self.n5
        )

    @property
    def total_adults(self) -> float:
        return self.adult_female + self.adult_male

    @property
    def total_population(self) -> float:
        return (
            self.eggs +
            self.total_nymphs +
            self.total_adults
        )

    def as_dict(self) -> dict:
        """Return a serialisable representation."""

        return {
            "date": self.simulation_date.isoformat(),
            "eggs": self.eggs,
            "n1": self.n1,
            "n2": self.n2,
            "n3": self.n3,
            "n4": self.n4,
            "n5": self.n5,
            "adult_female": self.adult_female,
            "adult_male": self.adult_male,
            "generation": self.generation,
            "degree_days": self.accumulated_degree_days,
            "growth_rate": self.population_growth_rate,
            "uncertainty": self.uncertainty,
            "total_population": self.total_population,
        }