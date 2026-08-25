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


def test_adult_suppression_scenario_reports_daylength():
    request = SimulationRequest(
        location="malua",
        initialization="overwintering_adults",
        initial_eggs=0,
        initial_adult_females_by_age={30: 50},
        initial_adult_males_by_age={30: 50},
        seasonal_activation="central",
        start_date="2024-07-01",
        end_date="2024-07-02",
    )

    result = simulate(request)

    assert result["seasonal_activation"] == "central"
    assert result["seasonal_latitude"] == -28.8
    assert all(row["daylength_hours"] for row in result["results"])
    assert all(
        0.0 <= row["reproductive_activation"] <= 1.0
        for row in result["results"]
    )


def test_orchard_coordinate_overrides_are_accepted():
    request = SimulationRequest(
        location="northern_nsw_01",
        start_date="2025-08-01",
        end_date="2025-08-03",
        live_latitude=-28.86,
        live_longitude=153.46,
        seasonal_latitude_override=-28.86,
    )

    assert request.live_latitude == -28.86
    assert request.live_longitude == 153.46
    assert request.seasonal_latitude_override == -28.86
