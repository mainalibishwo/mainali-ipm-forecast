from datetime import date

import pytest

from backend.engine.seasonality import (
    NoSeasonalSuppression,
    SmoothDaylengthActivation,
    bounded_activation,
    build_daylength_sensitivity_profile,
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


def test_daylength_activation_is_smooth_and_seasonal():
    model = SmoothDaylengthActivation(
        latitude_degrees=-28.8,
        lower_daylength_hours=10.75,
        upper_daylength_hours=12.0,
        winter_floor=0.025,
    )

    winter = model.activation(date(2024, 6, 21), 15.0)
    late_winter = model.activation(date(2024, 8, 15), 15.0)
    spring = model.activation(date(2024, 10, 15), 15.0)

    assert 0.0 <= winter <= late_winter < spring <= 1.0

    adjacent = [
        model.activation(date(2024, 9, day), 20.0)
        for day in range(1, 16)
    ]
    assert max(
        abs(right - left)
        for left, right in zip(adjacent, adjacent[1:])
    ) < 0.05


def test_profile_does_not_double_count_temperature():
    model = build_daylength_sensitivity_profile("central", -28.8)

    cool = model.activation(date(2024, 9, 15), 15.0)
    warm = model.activation(date(2024, 9, 15), 30.0)

    assert cool == warm


def test_envelope_order_in_winter():
    values = {
        name: build_daylength_sensitivity_profile(name, -28.8).activation(
            date(2024, 7, 15),
            18.0,
        )
        for name in ("conservative", "central", "permissive")
    }

    assert values["conservative"] <= values["central"] <= values["permissive"]
