"""Transparent monitoring-risk framework for the grower dashboard.

This module deliberately separates regional population activity, crop exposure
and orchard evidence.  It does not estimate economic loss or recommend
treatment.  Keeping the rules in Python makes the decision layer testable and
versionable rather than leaving it only as interface wording.
"""

from __future__ import annotations


ACTIVITY_BANDS = (
    (10.0, "Low"),
    (30.0, "Moderate"),
    (70.0, "High"),
    (float("inf"), "Very high"),
)

ACTIVE_CROP_STAGES = {
    "inflorescence",
    "flowering",
    "early_fruit",
    "nut_development",
}

PRIORITIES = (
    "Routine monitoring",
    "Enhanced monitoring",
    "High monitoring",
    "Very high monitoring",
)


def activity_band(index: float) -> str:
    """Translate the within-season relative index into a communication band."""

    value = min(100.0, max(0.0, float(index)))
    return next(label for upper, label in ACTIVITY_BANDS if value < upper)


def activity_direction(change_14d: float) -> str:
    """Use the same two-index-point stability rule as the dashboard."""

    if change_14d > 2.0:
        return "Increasing"
    if change_14d < -2.0:
        return "Decreasing"
    return "Stable"


def _base_priority(index: float, change_14d: float, crop_stage: str) -> int | None:
    if crop_stage == "unknown":
        return None
    if crop_stage == "post_harvest":
        return 0

    band = activity_band(index)
    increasing = activity_direction(change_14d) == "Increasing"
    active_tissue = crop_stage in ACTIVE_CROP_STAGES

    if active_tissue and band == "Very high":
        return 3
    if active_tissue and band == "High":
        return 2
    if active_tissue and (band == "Moderate" or increasing):
        return 1
    if crop_stage == "maturation" and band in {"High", "Very high"}:
        return 1
    return 0


def assess_monitoring_risk(
    *,
    activity_index: float,
    change_14d: float,
    crop_stage: str,
    bugs_observed: float | None = None,
    trees_sampled: int | None = None,
    damaged_nuts: int | None = None,
    nuts_examined: int | None = None,
) -> dict[str, object]:
    """Return a transparent, non-economic monitoring-risk assessment.

    A current live-bug detection can escalate the monitoring priority, while a
    non-detection never proves absence.  Nut injury is retained as supporting
    crop evidence because it may have accumulated before the forecast date.
    """

    if not 0 <= activity_index <= 100:
        raise ValueError("activity_index must be between 0 and 100")
    if crop_stage not in ACTIVE_CROP_STAGES | {
        "unknown", "maturation", "post_harvest"
    }:
        raise ValueError("unknown crop_stage")
    if (bugs_observed is None) != (trees_sampled is None):
        raise ValueError("bugs_observed and trees_sampled must be supplied together")
    if bugs_observed is not None and (bugs_observed < 0 or trees_sampled <= 0):
        raise ValueError("field counts require bugs >= 0 and trees > 0")
    if (damaged_nuts is None) != (nuts_examined is None):
        raise ValueError("damaged_nuts and nuts_examined must be supplied together")
    if damaged_nuts is not None and not 0 <= damaged_nuts <= nuts_examined:
        raise ValueError("require 0 <= damaged_nuts <= nuts_examined")

    band = activity_band(activity_index)
    direction = activity_direction(change_14d)
    rank = _base_priority(activity_index, change_14d, crop_stage)

    if crop_stage == "unknown":
        exposure = "Not assessed"
        exposure_basis = "Select the current orchard crop stage."
    elif crop_stage == "post_harvest":
        exposure = "Seasonal carryover context"
        exposure_basis = "No susceptible crop stage was selected."
    elif crop_stage == "maturation":
        exposure = f"{band} late-season overlap"
        exposure_basis = "Confirm current feeding because visible injury may lag exposure."
    else:
        exposure = f"{band} crop exposure"
        exposure_basis = "Susceptible reproductive tissue is present."

    if bugs_observed is None:
        field_evidence = "Not entered"
        field_basis = "Regional forecast only; enter a current consistent field sample when available."
    elif bugs_observed > 0:
        field_evidence = "Live bugs detected"
        field_basis = f"{bugs_observed:g} FSB/BSB observed across {trees_sampled} sampled trees."
        if rank is not None and crop_stage != "post_harvest":
            rank = max(rank, 2)
    elif trees_sampled >= 20:
        field_evidence = "Not detected in current sample"
        field_basis = (
            f"No FSB/BSB detected across {trees_sampled} sampled trees; "
            "repeat sampling because non-detection is not proof of absence."
        )
    else:
        field_evidence = "Limited non-detection"
        field_basis = (
            f"No FSB/BSB detected across {trees_sampled} sampled trees; "
            "the small sample provides limited evidence."
        )

    if damaged_nuts is None:
        damage_evidence = "Not entered"
        damage_basis = "Nut damage has not been added to the interpretation."
    elif damaged_nuts > 0:
        percent = 100.0 * damaged_nuts / nuts_examined
        damage_evidence = "Crop injury detected"
        damage_basis = (
            f"{damaged_nuts} of {nuts_examined} examined nuts ({percent:.1f}%) "
            "were recorded as FSB/BSB damaged; injury may pre-date today's population."
        )
    else:
        damage_evidence = "No injury detected in current nut sample"
        damage_basis = (
            f"No FSB/BSB injury recorded among {nuts_examined} examined nuts; "
            "retain the denominator and continue stage-appropriate checks."
        )

    priority = "Not assessed" if rank is None else PRIORITIES[rank]
    if crop_stage == "post_harvest":
        priority = "Seasonal surveillance"

    if priority in {"High monitoring", "Very high monitoring"}:
        action = "Prioritise repeated orchard inspection for live bugs and fresh feeding injury."
    elif priority == "Enhanced monitoring":
        action = "Increase monitoring frequency, including edges and known hotspots."
    elif priority == "Seasonal surveillance":
        action = "Use the forecast to follow carryover rather than as a crop-treatment signal."
    elif priority == "Routine monitoring":
        action = "Continue consistent routine monitoring and review if activity increases."
    else:
        action = "Select the crop stage before interpreting crop exposure."

    return {
        "framework_version": "MIFE monitoring-risk v0.2",
        "model_type": "Transparent rule-based monitoring-risk model",
        "regional_activity": {
            "index": round(activity_index, 1),
            "band": band,
            "direction": direction,
            "change_14d": round(change_14d, 1),
        },
        "crop_exposure": {
            "level": exposure,
            "basis": exposure_basis,
        },
        "orchard_evidence": {
            "live_insects": field_evidence,
            "live_insects_basis": field_basis,
            "nut_damage": damage_evidence,
            "nut_damage_basis": damage_basis,
        },
        "monitoring_priority": priority,
        "recommended_action": action,
        "scientific_boundary": (
            "Monitoring priority is not a damage probability, economic threshold "
            "or pesticide-treatment recommendation."
        ),
    }
