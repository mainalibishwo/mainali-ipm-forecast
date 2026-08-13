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

Run locally with:

```bash
pip install -r requirements.txt
uvicorn backend.api:app --host 0.0.0.0 --port 8000
```

Then open `http://localhost:8000`.

The dashboard offers stored research weather for reproducible runs and live
regional weather for operational forecasts. Live mode merges Open-Meteo data
at representative regional coordinates into de-identified regional series.
Malua, Knockrow and Dorey remain validation series and are deliberately
excluded from live forecasting. See `docs/MIFE_live_weather_protocol.md`.

## Validation

```bash
python -m pytest -q
python -m scripts.run_mife_initialization_sensitivity
python -m scripts.run_mife_field_validation
python -m scripts.plot_mife_field_diagnostics
```
