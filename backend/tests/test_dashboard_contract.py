from pathlib import Path

from backend.api import LOCATIONS, locations, manual


def test_all_operational_regions_have_seasonal_latitude():
    operational = [key for key in LOCATIONS if key != "demo"]
    assert operational
    assert all("seasonal_latitude" in LOCATIONS[key] for key in operational)


def test_locations_endpoint_marks_seasonal_support():
    rows = locations()["locations"]
    by_id = {row["id"]: row for row in rows}
    assert by_id["demo"]["supports_seasonal_forecast"] is False
    assert by_id["malua"]["supports_seasonal_forecast"] is True
    assert by_id["malua"]["supports_live_weather"] is False
    assert by_id["malua"]["series_role"] == "validation"
    assert by_id["malua"]["weather_start"] == "2024-01-01"
    assert by_id["malua"]["weather_end"] == "2026-02-28"
    assert by_id["wide_bay_gympie_01"]["supports_live_weather"] is True
    assert by_id["wide_bay_gympie_01"]["series_role"] == "regional"


def test_dashboard_labels_field_density_as_sampling_equivalent():
    dashboard = Path("frontend/index.html").read_text()
    assert "Sampling-equivalent bugs/ha" in dashboard
    assert "perTree*density" in dashboard
    assert "10000/(row*within)" in dashboard
    assert "Not a true whole-canopy population estimate" in dashboard
    assert "modelled autumn carryover signal" in dashboard
    assert "not automatically the period of greatest crop damage" in dashboard
    assert "displayDate(peaks[0])" in dashboard
    assert "year:'numeric'" in dashboard
    assert "normalizeComposition" in dashboard
    assert "Regional population outlook" in dashboard
    assert "Current regional pressure" in dashboard
    assert "7- and 14-day outlook" in dashboard
    assert "Forecast weather available through" in dashboard
    assert "Modelled seasonal population peak" in dashboard
    assert "forecastPeriodPlugin" in dashboard
    assert "index===final" in dashboard
    assert "rescaled to total 100% each day" in dashboard
    assert "156 multi-season events" in dashboard
    assert "BBCH 50–59 — inflorescence emergence" in dashboard
    assert "BBCH 60–69 — flowering" in dashboard
    assert "BBCH 00–39" not in dashboard
    assert "vegetative:{" not in dashboard
    assert "cropGuidance" in dashboard
    assert "Crop-risk interpretation" in dashboard
    assert "seasonal carryover and overwintering population development" in dashboard
    assert "does not alter insect biology or the forecast curve" in dashboard
    assert "Hort Innovation macadamia research and development levy" in dashboard
    assert "Christopher Themsen, Chris Fuller and Jarrah Coates" in dashboard
    assert "Cervantes Agritech" in dashboard
    assert "/assets/macquarie-university-logo.svg" in dashboard
    assert "/assets/hort-innovation-logo.svg" in dashboard
    assert Path("frontend/assets/macquarie-university-logo.svg").is_file()
    assert Path("frontend/assets/hort-innovation-logo.svg").is_file()


def test_grower_manual_covers_model_and_decision_boundaries():
    response = manual()
    assert response.path.endswith("frontend/manual.html")
    guide = Path("frontend/manual.html").read_text()
    for required in (
        "Process snapshot",
        "Why nine scenarios?",
        "Sampling-equivalent bugs/ha",
        "not a statistical confidence interval",
        "does not provide a pesticide recommendation",
        "Print or save as PDF",
        "Funding and acknowledgements",
        "Christopher Themsen, Chris Fuller and Jarrah Coates",
        "Cervantes Agritech",
        "156 de-identified orchard/block-date events",
        "18 Northern NSW events from 2025–26",
        "AUC 0.731",
        "not proof of operational accuracy",
        "rescaled to total exactly 100% each day",
        "Macadamia BBCH crop-stage guide",
        "BBCH 00–39 is intentionally omitted",
        "Autumn carryover forecast",
        "Inflorescence emergence",
        "Fruit set/very young nuts",
        "calendar timing must not be transferred directly",
        "Roppolo et al. (2024)",
        "Current regional pressure and direction",
        "7- and 14-day outlook",
        "actual available end date",
    ):
        assert required in guide
