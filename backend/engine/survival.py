"""
survival.py

Stage-specific survival functions for the Mainali IPM Forecast Engine (MIFE).

This module converts experimentally measured conditional survival into
daily survival probabilities.
"""

from __future__ import annotations

import math


class SurvivalModel:
    """
    Daily survival model.

    This implementation uses conditional survival measured over an entire
    life stage and converts it to an equivalent daily survival probability.
    """

    @staticmethod
    def daily_survival_probability(
        conditional_survival: float,
        stage_duration_days: float,
    ) -> float:
        """
        Convert whole-stage survival to daily survival.

        Example
        -------
        Stage survival = 0.90
        Stage duration = 10 days

        Daily survival = 0.90 ** (1/10)
        """

        if not 0.0 <= conditional_survival <= 1.0:
            raise ValueError(
                "conditional_survival must be between 0 and 1."
            )

        if stage_duration_days <= 0:
            raise ValueError(
                "stage_duration_days must be greater than zero."
            )

        return math.pow(
            conditional_survival,
            1.0 / stage_duration_days,
        )

    @staticmethod
    def survivors(
        population: float,
        daily_survival_probability: float,
    ) -> float:
        """
        Number surviving one day.
        """

        if population < 0:
            raise ValueError(
                "population cannot be negative."
            )

        if not 0.0 <= daily_survival_probability <= 1.0:
            raise ValueError(
                "daily_survival_probability must lie between 0 and 1."
            )

        return population * daily_survival_probability