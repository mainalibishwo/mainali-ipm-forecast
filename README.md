# MIFE — Mainali IPM Forecast Engine

MIFE is a weather-driven research decision-support system for *Amblypelta*
population phenology and relative population pressure.

## Scientific scope

- frozen temperature-dependent development, survival and fecundity;
- overwintering-adult initialization;
- preregistered seasonal reproductive-activation envelope;
- Queensland and Northern NSW regional weather series;
- 21-event Malua, Knockrow and Dorey field validation;
- optional external adult-movement research boundary, inactive by default.

MIFE output is not calibrated as bugs per tree, an economic threshold or a
pesticide recommendation.

## Dashboard

The dashboard reports all nine preregistered activation × adult-age scenarios.
Its central line is their median and its shading is their full range, not a
confidence interval. Crop susceptibility is a user-supplied exposure overlay
and does not alter insect biology.

The grower view also provides a **seasonal activity calendar**. It translates
the median activity trajectory, seven-day direction and modelled egg, nymph and
adult composition into plain-language seasonal phases. These phases summarise
overlapping cohorts; they are not discrete generations, observed events,
damage thresholds or treatment triggers.

Run locally with:

```bash
pip install -r requirements.txt
uvicorn backend.api:app --host 0.0.0.0 --port 8000
```

Then open `http://localhost:8000`.

For the grower-pilot production architecture and release checklist, see
`docs/MIFE_grower_pilot_deployment.md`. The repository includes a non-root
Docker image and a Render service blueprint; Cloudflare remains the DNS, TLS
and edge-protection layer for `forecast.mainaliipm.com`.
The initial blueprint uses free pilot hosting and can be upgraded without
changing the public URL or biological model.
The dashboard links to a printable grower manual at `/manual`, covering the
model structure, process snapshot, interpretation and decision boundaries.

The grower dashboard uses live regional weather for operational forecasts.
Stored research weather remains available internally for reproducible model
testing and retrospective validation, but is not shown as a grower-selectable
option. Live mode merges Open-Meteo data at representative regional coordinates
into de-identified regional series.
Malua, Knockrow and Dorey remain validation series and are deliberately
excluded from live forecasting. See `docs/MIFE_live_weather_protocol.md`.

The field-sampling panel combines FSB and BSB and converts a consistent
tree-based observation to **sampling-equivalent bugs/ha** using editable
orchard tree density. A preliminary Northern NSW count-rate calibration,
developed from research drop-sheet observations, is updated with the current
orchard sample and carried along the regional 7- and 14-day trajectory. The
four-tree research design remains only an internal prior weight; it is not a
required grower sampling unit. Resulting values are planning estimates, not a
whole-orchard census, economic threshold or treatment trigger. Recent
FSB/BSB-targeted management is flagged but is not assigned an unvalidated
efficacy correction. See
`docs/MIFE_field_adjustment_protocol.md`.

An optional nut-damage check reports FSB/BSB injury as a numerator,
denominator, percentage and approximate binomial interval. Damage remains
separate from the live-insect forecast because it can accumulate before the
sampling date.

The Northern NSW March–April maximum is labelled a **modelled autumn population
peak**, distinct from harvest timing and crop-damage risk. The literature and
required March–May field-validation protocol are documented in
`docs/MIFE_autumn_peak_evidence_and_validation.md`. No biological parameter was
adjusted following this review.

## Validation

```bash
python -m pytest -q
python -m scripts.run_mife_initialization_sensitivity
python -m scripts.run_mife_field_validation
python -m scripts.plot_mife_field_diagnostics
```
