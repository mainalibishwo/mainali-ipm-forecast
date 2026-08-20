import pytest

from backend.risk import activity_band, assess_monitoring_risk


@pytest.mark.parametrize(
    ("index", "expected"),
    [(0, "Low"), (9.9, "Low"), (10, "Moderate"), (30, "High"), (70, "Very high"), (100, "Very high")],
)
def test_activity_bands_match_grower_communication(index, expected):
    assert activity_band(index) == expected


def test_high_activity_and_susceptible_crop_produce_high_monitoring():
    result = assess_monitoring_risk(
        activity_index=45,
        change_14d=4,
        crop_stage="early_fruit",
    )
    assert result["crop_exposure"]["level"] == "High crop exposure"
    assert result["monitoring_priority"] == "High monitoring"
    assert "not a damage probability" in result["scientific_boundary"]


def test_current_detection_escalates_monitoring_but_damage_remains_context():
    result = assess_monitoring_risk(
        activity_index=5,
        change_14d=0,
        crop_stage="nut_development",
        bugs_observed=1,
        trees_sampled=30,
        damaged_nuts=2,
        nuts_examined=40,
    )
    assert result["monitoring_priority"] == "High monitoring"
    assert result["orchard_evidence"]["live_insects"] == "Live bugs detected"
    assert "may pre-date" in result["orchard_evidence"]["nut_damage_basis"]


def test_non_detection_does_not_claim_absence_or_cancel_regional_signal():
    result = assess_monitoring_risk(
        activity_index=80,
        change_14d=-4,
        crop_stage="flowering",
        bugs_observed=0,
        trees_sampled=30,
    )
    assert result["monitoring_priority"] == "Very high monitoring"
    assert "not proof of absence" in result["orchard_evidence"]["live_insects_basis"]


def test_unknown_crop_stage_keeps_activity_but_does_not_assess_exposure():
    result = assess_monitoring_risk(
        activity_index=80,
        change_14d=4,
        crop_stage="unknown",
    )
    assert result["regional_activity"]["band"] == "Very high"
    assert result["monitoring_priority"] == "Not assessed"


def test_incomplete_field_pair_is_rejected():
    with pytest.raises(ValueError, match="supplied together"):
        assess_monitoring_risk(
            activity_index=20,
            change_14d=0,
            crop_stage="flowering",
            bugs_observed=1,
        )
