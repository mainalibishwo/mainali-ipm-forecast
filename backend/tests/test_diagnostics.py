from datetime import date

import pytest

from backend.engine.diagnostics import Diagnostics
from backend.engine.simulation import SimulationState


def make_state(
    egg=0.0,
    n1=0.0,
    n2=0.0,
    n3=0.0,
    n4=0.0,
    n5=0.0,
    females=None,
    males=None,
    degree_days=0.0,
):
    return SimulationState(
        simulation_date=date(2026, 8, 10),
        immature={
            "Egg": egg,
            "N1": n1,
            "N2": n2,
            "N3": n3,
            "N4": n4,
            "N5": n5,
        },
        adult_female_by_age=females or {0: 0.0},
        adult_male_by_age=males or {0: 0.0},
        cumulative_degree_days=degree_days,
    )


def test_population_composition():
    state = make_state(
        egg=10,
        n1=20,
        females={0: 5},
        males={0: 3},
    )

    composition = Diagnostics.composition(state)

    assert composition.immature == 30
    assert composition.adult_female == 5
    assert composition.adult_male == 3
    assert composition.adults == 8
    assert composition.total == 38


def test_mass_balance_with_births_and_mortality():
    opening = make_state(
        egg=50,
        n1=50,
    )

    closing = make_state(
        egg=55,
        n1=40,
    )

    balance = Diagnostics.mass_balance(
        opening,
        closing,
        births=10,
    )

    assert balance.opening_population == 100
    assert balance.births == 10
    assert balance.closing_population == 95

    assert balance.inferred_biological_deaths == 15
    assert abs(balance.balance_error) < 1e-12
    assert balance.is_balanced


def test_stage_transition_does_not_change_total_population():
    opening = make_state(
        egg=100,
    )

    closing = make_state(
        egg=80,
        n1=20,
    )

    balance = Diagnostics.mass_balance(
        opening,
        closing,
    )

    assert balance.closing_population == 100
    assert balance.inferred_biological_deaths == 0
    assert balance.is_balanced


def test_validate_state_accepts_valid_state():
    state = make_state(
        egg=100,
        n1=20,
        females={0: 10},
        degree_days=25,
    )

    Diagnostics.validate_state(state)


def test_validate_state_rejects_negative_population():
    state = make_state(
        egg=-1,
    )

    with pytest.raises(
        ValueError,
        match="negative abundance",
    ):
        Diagnostics.validate_state(state)


def test_validate_state_rejects_negative_degree_days():
    state = make_state(
        degree_days=-1,
    )

    with pytest.raises(
        ValueError,
        match="degree-days",
    ):
        Diagnostics.validate_state(state)


def test_negative_births_are_rejected():
    opening = make_state(egg=100)
    closing = make_state(egg=100)

    with pytest.raises(
        ValueError,
        match="births cannot be negative",
    ):
        Diagnostics.mass_balance(
            opening,
            closing,
            births=-1,
        )