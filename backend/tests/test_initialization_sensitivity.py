from scripts.run_mife_initialization_sensitivity import (
    ACTIVATION_PROFILES,
    AGE_BANDS,
    SITES,
    TOTAL_ADULTS,
    uniform_distribution,
)


def test_uniform_adult_distribution_conserves_abundance():
    distribution = uniform_distribution(50.0, range(0, 31))

    assert len(distribution) == 31
    assert abs(sum(distribution.values()) - 50.0) < 1e-10


def test_preregistered_ensemble_contains_81_runs():
    assert len(SITES) * len(ACTIVATION_PROFILES) * len(AGE_BANDS) * len(TOTAL_ADULTS) == 81
