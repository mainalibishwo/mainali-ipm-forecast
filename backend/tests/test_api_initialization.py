import pytest
from fastapi import HTTPException

from backend.api import SimulationRequest, simulate


def test_legacy_egg_request_remains_valid():
    request = SimulationRequest(
        location="malua",
        initial_eggs=100,
        start_date="2024-07-01",
        end_date="2024-07-02",
    )

    result = simulate(request)

    assert result["initialization"] == "eggs"
    assert result["initial_eggs"] == 100
    assert all(
        row["reproductive_activation"] == 1.0
        for row in result["results"]
    )


def test_overwintering_adult_request_is_supported():
    request = SimulationRequest(
        location="malua",
        initialization="overwintering_adults",
        initial_eggs=0,
        initial_adult_females_by_age={30: 50},
        initial_adult_males_by_age={30: 50},
        start_date="2024-07-01",
        end_date="2024-07-02",
    )

    result = simulate(request)

    assert result["initialization"] == "overwintering_adults"
    assert result["initial_eggs"] == 0
    assert result["initial_adult_females_by_age"] == {30: 50.0}
    assert result["initial_adult_males_by_age"] == {30: 50.0}


def test_adult_initialization_rejects_nonzero_eggs():
    request = SimulationRequest(
        location="malua",
        initialization="overwintering_adults",
        initial_eggs=100,
        initial_adult_females_by_age={30: 50},
        initial_adult_males_by_age={30: 50},
        start_date="2024-07-01",
        end_date="2024-07-02",
    )

    with pytest.raises(HTTPException) as exc_info:
        simulate(request)

    assert "initial_eggs=0" in str(exc_info.value.detail)
