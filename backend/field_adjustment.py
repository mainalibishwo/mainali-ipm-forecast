"""Transparent field-sampling calculations mirrored by the grower dashboard."""

from __future__ import annotations

from math import exp, sqrt


LOG_INTERCEPT = -2.5910446
LOG_INDEX_SLOPE = 0.14813414
PRIOR_TREE_STRENGTH = 4.0


def empirical_regional_rate(index: float) -> float:
    """Return preliminary combined FSB/BSB per-tree prior for an index value."""

    safe_index = max(0.0, float(index))
    return exp(LOG_INTERCEPT) * (1.0 + safe_index) ** LOG_INDEX_SLOPE


def field_adjusted_rate(
    bugs: float, trees: float, current_index: float, future_index: float
) -> dict[str, float]:
    """Update the regional prior and carry the local multiplier into the future."""

    if bugs < 0 or trees <= 0:
        raise ValueError("bugs must be non-negative and trees must be positive")
    prior_now = empirical_regional_rate(current_index)
    posterior_now = (PRIOR_TREE_STRENGTH * prior_now + bugs) / (
        PRIOR_TREE_STRENGTH + trees
    )
    local_multiplier = posterior_now / prior_now
    return {
        "observed_per_tree": bugs / trees,
        "posterior_per_tree": posterior_now,
        "future_per_tree": empirical_regional_rate(future_index) * local_multiplier,
    }


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    """Return a Wilson binomial interval as proportions."""

    if total <= 0 or successes < 0 or successes > total:
        raise ValueError("require 0 <= successes <= total and total > 0")
    proportion = successes / total
    denominator = 1.0 + z * z / total
    centre = (proportion + z * z / (2.0 * total)) / denominator
    half_width = (
        z
        * sqrt(
            proportion * (1.0 - proportion) / total
            + z * z / (4.0 * total * total)
        )
        / denominator
    )
    return max(0.0, centre - half_width), min(1.0, centre + half_width)
