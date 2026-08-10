"""
development.py

Stage progression logic for the Mainali IPM Forecast Engine (MIFE).

This module converts daily thermal development into biologically consistent
movement through Egg -> N1 -> N2 -> N3 -> N4 -> N5 -> Adult.
"""

from __future__ import annotations

from dataclasses import dataclass


STAGE_ORDER: tuple[str, ...] = (
    "Egg",
    "N1",
    "N2",
    "N3",
    "N4",
    "N5",
)


@dataclass(frozen=True, slots=True)
class StageTransition:
    """Result of one day's development within a stage."""

    remaining: float
    progressed: float

    def __post_init__(self) -> None:
        if self.remaining < 0:
            raise ValueError("remaining cannot be negative.")

        if self.progressed < 0:
            raise ValueError("progressed cannot be negative.")


class DevelopmentModel:
    """
    Daily stage-transition calculations.

    Daily development rate represents the fraction of mean stage development
    completed per day. A rate of 0.10 therefore corresponds to approximately
    one tenth of stage completion per day.
    """

    @staticmethod
    def transition(
        population: float,
        daily_development_rate: float,
    ) -> StageTransition:
        """
        Split a stage population into individuals remaining and progressing.

        The simple stage-total formulation is a first deterministic layer.
        Cohort/bin structure can later replace it without changing the public
        interface of the simulation engine.
        """

        if population < 0:
            raise ValueError("population cannot be negative.")

        if daily_development_rate < 0:
            raise ValueError(
                "daily_development_rate cannot be negative."
            )

        # A stage cannot progress by more than its entire population in one day.
        fraction = min(daily_development_rate, 1.0)

        progressed = population * fraction
        remaining = population - progressed

        return StageTransition(
            remaining=remaining,
            progressed=progressed,
        )

    @staticmethod
    def next_stage(stage: str) -> str:
        """Return the stage following the supplied immature stage."""

        if stage not in STAGE_ORDER:
            raise KeyError(f"Unknown immature stage: {stage!r}")

        index = STAGE_ORDER.index(stage)

        if index == len(STAGE_ORDER) - 1:
            return "Adult"

        return STAGE_ORDER[index + 1]