from datetime import date

import pytest

from backend.engine.seasonality import (
    NoSeasonalSuppression,
    bounded_activation,
    daylength_hours,
)


def test_southern_daylength_is_shorter_in_winter():
    latitude = -28.6
    winter = daylength_hours(date(2024, 6, 21), latitude)
    summer = daylength_hours(date(2024, 12, 21), latitude)

    assert 0.0 < winter < summer < 24.0


def test_reference_activation_preserves_frozen_core():
    model = NoSeasonalSuppression()

    assert bounded_activation(
        model,
        date(2024, 7, 1),
        18.0,
    ) == 1.0


def test_activation_outside_bounds_is_rejected():
    class InvalidActivation:
        def activation(self, calendar_date, temperature_c):
            del calendar_date, temperature_c
            return 1.01

    with pytest.raises(ValueError):
        bounded_activation(
            InvalidActivation(),
            date(2024, 7, 1),
            18.0,
        )
