from datetime import date

import pytest

from backend.engine.movement import AdultEntry, apply_adult_entry
from backend.engine.simulation import SimulationState


def state() -> SimulationState:
    return SimulationState(
        simulation_date=date(2024, 7, 1),
        immature={stage: 0.0 for stage in ("Egg", "N1", "N2", "N3", "N4", "N5")},
        adult_female_by_age={10: 4.0},
        adult_male_by_age={10: 3.0},
    )


def test_zero_entry_is_exact_reference():
    original = state()
    assert apply_adult_entry(original) is original
    assert apply_adult_entry(original, AdultEntry()) is original


def test_entry_adds_adults_without_modifying_immatures():
    original = state()
    updated = apply_adult_entry(
        original,
        AdultEntry(females=2.0, males=1.0, adult_age_days=10),
    )

    assert updated.adult_female_by_age[10] == 6.0
    assert updated.adult_male_by_age[10] == 4.0
    assert updated.immature == original.immature
    assert original.adult_female_by_age[10] == 4.0


@pytest.mark.parametrize(
    "entry",
    (
        AdultEntry(females=0.0, males=0.0),
        AdultEntry(females=1.0, males=2.0, adult_age_days=5),
    ),
)
def test_entry_total_is_auditable(entry):
    assert entry.total == entry.females + entry.males


def test_negative_entry_is_rejected():
    with pytest.raises(ValueError):
        AdultEntry(females=-1.0)
