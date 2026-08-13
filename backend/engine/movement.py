"""External adult-entry support for MIFE sensitivity experiments.

Movement is deliberately kept outside the frozen biological engine.  The
objects in this module do not infer entry from field observations and do not
contain a default immigration rate.  They only provide an explicit, auditable
way to add independently specified adult entrants after a daily biological
timestep.
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.engine.simulation import SimulationState


@dataclass(frozen=True)
class AdultEntry:
    """Externally specified adults entering the represented population."""

    females: float = 0.0
    males: float = 0.0
    adult_age_days: int = 0

    def __post_init__(self) -> None:
        if self.females < 0 or self.males < 0:
            raise ValueError("Adult entry abundance cannot be negative.")
        if self.adult_age_days < 0:
            raise ValueError("Adult entry age cannot be negative.")

    @property
    def total(self) -> float:
        return self.females + self.males


def apply_adult_entry(
    state: SimulationState,
    entry: AdultEntry | None = None,
) -> SimulationState:
    """Return ``state`` with external entrants added at their stated age.

    This function is intended to be called after the day's biological step.
    Entrants therefore do not survive, age or reproduce retrospectively on
    their day of entry.  With no entry, the exact original state object is
    returned, guaranteeing a strict zero-forcing reference.
    """

    if entry is None or entry.total == 0:
        return state

    females = dict(state.adult_female_by_age)
    males = dict(state.adult_male_by_age)
    age = entry.adult_age_days

    females[age] = females.get(age, 0.0) + entry.females
    males[age] = males.get(age, 0.0) + entry.males

    return SimulationState(
        simulation_date=state.simulation_date,
        immature=state.immature,
        adult_female_by_age=females,
        adult_male_by_age=males,
        cumulative_degree_days=state.cumulative_degree_days,
        immature_cohorts=state.immature_cohorts,
    )
