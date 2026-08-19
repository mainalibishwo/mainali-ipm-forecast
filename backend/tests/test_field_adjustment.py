import pytest

from backend.field_adjustment import (
    empirical_regional_rate,
    field_adjusted_rate,
    wilson_interval,
)


def test_four_tree_observation_updates_current_rate():
    result = field_adjusted_rate(bugs=2, trees=4, current_index=10, future_index=10)
    assert result["observed_per_tree"] == pytest.approx(0.5)
    assert result["posterior_per_tree"] > empirical_regional_rate(10)
    assert result["future_per_tree"] == pytest.approx(result["posterior_per_tree"])


def test_zero_sample_reduces_but_does_not_zero_outlook():
    result = field_adjusted_rate(bugs=0, trees=4, current_index=10, future_index=30)
    assert result["posterior_per_tree"] > 0
    assert result["future_per_tree"] > 0


def test_more_sampling_effort_gives_the_observation_more_weight():
    small = field_adjusted_rate(bugs=0, trees=4, current_index=10, future_index=10)
    large = field_adjusted_rate(bugs=0, trees=20, current_index=10, future_index=10)
    assert large["posterior_per_tree"] < small["posterior_per_tree"]


def test_regional_increase_carries_into_adjusted_outlook():
    current = field_adjusted_rate(bugs=1, trees=4, current_index=5, future_index=5)
    future = field_adjusted_rate(bugs=1, trees=4, current_index=5, future_index=50)
    assert future["future_per_tree"] > current["future_per_tree"]


def test_wilson_interval_contains_observed_proportion():
    lower, upper = wilson_interval(3, 40)
    assert lower < 3 / 40 < upper
    assert 0 <= lower <= upper <= 1


@pytest.mark.parametrize("successes,total", [(-1, 10), (11, 10), (0, 0)])
def test_wilson_rejects_invalid_counts(successes, total):
    with pytest.raises(ValueError):
        wilson_interval(successes, total)
