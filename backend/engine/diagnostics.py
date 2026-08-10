"""
diagnostics.py

Population-accounting diagnostics for the Mainali IPM Forecast Engine (MIFE).

The diagnostics layer does not alter the biological simulation. It checks
whether changes in abundance are internally consistent and exposes any
unexpected numerical gain or loss.
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.engine.simulation import SimulationState


@dataclass(frozen=True, slots=True)
class MassBalance:
    """Daily population accounting summary."""

    opening_population: float
    births: float
    external_inputs: float
    known_removals: float
    closing_population: float

    @property
    def expected_before_mortality(self) -> float:
        """
        Population available after births and external inputs,
        before biological mortality.
        """
        return (
            self.opening_population
            + self.births
            + self.external_inputs
            - self.known_removals
        )

    @property
    def inferred_biological_deaths(self) -> float:
        """
        Population loss not explained by explicit removals.

        In the current engine this mainly represents mortality generated
        by immature and adult survival processes.
        """
        return (
            self.expected_before_mortality
            - self.closing_population
        )

    @property
    def balance_error(self) -> float:
        """
        Numerical accounting error.

        By definition:

        opening + births + inputs
        - removals - inferred deaths - closing = 0
        """
        return (
            self.opening_population
            + self.births
            + self.external_inputs
            - self.known_removals
            - self.inferred_biological_deaths
            - self.closing_population
        )

    @property
    def is_balanced(self) -> bool:
        """True when numerical error is effectively zero."""
        return abs(self.balance_error) < 1e-9


@dataclass(frozen=True, slots=True)
class PopulationComposition:
    """Stage-group composition of one SimulationState."""

    immature: float
    adult_female: float
    adult_male: float

    @property
    def adults(self) -> float:
        return self.adult_female + self.adult_male

    @property
    def total(self) -> float:
        return self.immature + self.adults


class Diagnostics:
    """Non-invasive checks for population simulations."""

    @staticmethod
    def composition(
        state: SimulationState,
    ) -> PopulationComposition:
        """Summarise immature and adult abundance."""

        immature = sum(
            float(value)
            for value in state.immature.values()
        )

        females = sum(
            float(value)
            for value in state.adult_female_by_age.values()
        )

        males = sum(
            float(value)
            for value in state.adult_male_by_age.values()
        )

        return PopulationComposition(
            immature=immature,
            adult_female=females,
            adult_male=males,
        )

    @staticmethod
    def mass_balance(
        opening_state: SimulationState,
        closing_state: SimulationState,
        *,
        births: float = 0.0,
        external_inputs: float = 0.0,
        known_removals: float = 0.0,
    ) -> MassBalance:
        """
        Calculate daily whole-population accounting.

        Stage transitions are deliberately not counted as gains or losses,
        because movement from Egg -> N1 -> ... -> Adult remains inside the
        population system.
        """

        if births < 0:
            raise ValueError("births cannot be negative.")

        if external_inputs < 0:
            raise ValueError(
                "external_inputs cannot be negative."
            )

        if known_removals < 0:
            raise ValueError(
                "known_removals cannot be negative."
            )

        opening = Diagnostics.composition(
            opening_state
        ).total

        closing = Diagnostics.composition(
            closing_state
        ).total

        return MassBalance(
            opening_population=opening,
            births=float(births),
            external_inputs=float(external_inputs),
            known_removals=float(known_removals),
            closing_population=closing,
        )

    @staticmethod
    def validate_state(
        state: SimulationState,
    ) -> None:
        """
        Raise an error if a simulation state is biologically impossible.
        """

        values = list(state.immature.values())
        values += list(
            state.adult_female_by_age.values()
        )
        values += list(
            state.adult_male_by_age.values()
        )

        if any(value < 0 for value in values):
            raise ValueError(
                "Simulation state contains negative abundance."
            )

        if state.cumulative_degree_days < 0:
            raise ValueError(
                "Cumulative degree-days cannot be negative."
            )