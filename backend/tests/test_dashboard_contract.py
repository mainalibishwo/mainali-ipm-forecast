from pathlib import Path

from backend.api import LOCATIONS, locations, manual


def test_all_operational_regions_have_seasonal_latitude():
    operational = [key for key in LOCATIONS if key != "demo"]
    assert operational
    assert all("seasonal_latitude" in LOCATIONS[key] for key in operational)


def test_locations_endpoint_marks_seasonal_support():
    rows = locations()["locations"]
    by_id = {row["id"]: row for row in rows}
    assert "western_downs_01" not in by_id
    assert by_id["demo"]["supports_seasonal_forecast"] is False
    assert by_id["malua"]["supports_seasonal_forecast"] is True
    assert by_id["malua"]["supports_live_weather"] is False
    assert by_id["malua"]["series_role"] == "validation"
    assert by_id["malua"]["weather_start"] == "2024-01-01"
    assert by_id["malua"]["weather_end"] == "2026-02-28"
    assert by_id["wide_bay_gympie_01"]["supports_live_weather"] is True
    assert by_id["wide_bay_gympie_01"]["series_role"] == "regional"
    assert by_id["wide_bay_gympie_01"]["grower_visible"] is True
    assert by_id["wide_bay_gympie_02"]["grower_visible"] is False
    assert by_id["northern_nsw_01"]["name"] == "Northern NSW — near Alstonville"
    assert by_id["northern_nsw_01"]["live_latitude"] == -28.80
    assert by_id["northern_nsw_01"]["live_longitude"] == 153.40
    assert by_id["northern_nsw_02"]["grower_visible"] is False


def test_dashboard_separates_regional_field_and_damage_outputs():
    dashboard = Path("frontend/index.html").read_text()
    assert "Sampling-equivalent bugs/ha" in dashboard
    assert "Stored research record — retrospective" not in dashboard
    assert 'id="weatherSource" type="hidden" value="live"' in dashboard
    assert "LOW ACTIVITY" not in dashboard
    assert "ACTIVITY STATUS — RUN OUTLOOK" in dashboard
    assert "Live regional comparison" in dashboard
    assert "fetchBrowserWeather" in dashboard
    assert "live_weather_days" in dashboard
    assert "Regional comparison unavailable" in dashboard
    assert "Seasonal activity calendar" in dashboard
    assert "Current modelled activity period" in dashboard
    assert "Population build-up" in dashboard
    assert "seasonalActivityWindows" in dashboard
    assert "smoothActivity(activity,radius=7)" in dashboard
    assert "Modelled life-stage composition is shown separately" in dashboard
    assert "Approx." in dashboard
    assert "not discrete generations" in dashboard
    assert "Nymph population" in dashboard
    assert "Adult population" in dashboard
    assert "shared maximum = 100" in dashboard
    assert "x.grower_visible!==false" in dashboard
    assert "Field-adjusted in 7 days" in dashboard
    assert "Field-adjusted in 14 days" in dashboard
    assert "FSB/BSB observed" in dashboard
    assert "priorTreeStrength:4" in dashboard
    assert "fieldAdjustedRate" in dashboard
    assert "Optional nut-damage check" in dashboard
    assert "Approx. 95% interval" in dashboard
    assert "wilson(success,total)" in dashboard
    assert "Trees per hectare" in dashboard
    assert "treeDensity(row,within)" in dashboard
    assert "Observed per four-tree set" not in dashboard
    assert "modelled autumn carryover signal" in dashboard
    assert "not automatically the period of greatest crop damage" in dashboard
    assert "displayDate(peaks[0])" in dashboard
    assert "year:'numeric'" in dashboard
    assert "normalizeComposition" in dashboard
    assert "Regional population outlook" in dashboard
    assert "Population activity today" in dashboard
    assert "Predicted activity in 7 and 14 days" in dashboard
    assert "Live weather available through" in dashboard
    assert "Predicted seasonal peak window" in dashboard
    assert "forecastPeriodPlugin" in dashboard
    assert "index===final" in dashboard
    assert "Reference starting adults" not in dashboard
    assert "total=100" in dashboard
    assert "Mainali IPM Forecast Engine" not in dashboard
    assert "Spotting bug phenology and relative population pressure" in dashboard
    assert "rescaled to total 100% each day" in dashboard
    assert "156 multi-season events" in dashboard
    assert "BBCH 50–59 — inflorescence emergence" in dashboard
    assert "BBCH 60–69 — flowering" in dashboard
    assert "BBCH 00–39" not in dashboard
    assert "vegetative:{" not in dashboard
    assert "cropGuidance" in dashboard
    assert "What this means for monitoring" in dashboard
    assert "What the 0–100 index means" in dashboard
    assert "fruitspotting bug (FSB" in dashboard
    assert "banana spotting bug (BSB" in dashboard
    assert "Population activity index (0–100)" in dashboard
    assert "Relative mobile pressure" not in dashboard
    assert "Show regional outlook" in dashboard
    assert "Low: 0 to &lt;10" in dashboard
    assert "Moderate: 10 to &lt;30" in dashboard
    assert "High: 30 to &lt;70" in dashboard
    assert "Very high: 70–100" in dashboard
    assert "Changes under 2 index points are described as stable" in dashboard
    assert "s.value='malua'" not in dashboard
    assert "seasonal carryover and overwintering population development" in dashboard
    assert "does not change the predicted population" in dashboard
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
    assert "Mainali IPM Forecast Engine" not in guide
    for required in (
        "Five steps for growers",
        "Why nine scenarios?",
        "Sampling-equivalent bugs/ha",
        "Field-adjusted sampling outlook",
        "Nut-damage check",
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
        "Population activity today and direction",
        "Predicted activity in 7 and 14 days",
        "actual available end date",
        "fixed internal reference population of 100 adults",
        "Which spotting bugs are covered?",
        "Population activity index (0–100)",
        "Most field validation evidence is for FSB",
        "Activity-level guide",
        "communication bands for the relative index",
        "Seasonal activity calendar",
        "15-day moving average",
        "Life-stage composition is intentionally kept separate",
        "not evidence of one generation",
    ):
        assert required in guide
