# MIFE live regional weather protocol

## Purpose

MIFE can extend its stored, reproducible weather records with recent and
forecast daily weather from Open-Meteo. This changes only the environmental
input. It does not change biological parameters, model equations,
initialisation bands or seasonal-activation profiles.

## Operational boundary

- Live mode is available only for de-identified regional series.
- Malua, Knockrow and Dorey remain named field-validation series and cannot be
  selected in live mode.
- A regional forecast is not an orchard-specific forecast. Users must combine
  it with local monitoring and crop phenology.
- The adapter requests daily minimum temperature, maximum temperature and
  precipitation in the `Australia/Sydney` timezone.
- Ten recent days and up to 16 forecast days are requested. Live values replace
  stored values on overlapping dates so the transition is continuous.
- Responses are cached for 15 minutes. Provider failures are reported; the
  application does not silently substitute stored weather.

## Representative coordinates

| MIFE region | Latitude | Longitude |
|---|---:|---:|
| Wide Bay–Gympie | -25.90 | 152.60 |
| Glass House Mountains | -26.90 | 152.95 |
| Bundaberg Region | -24.87 | 152.35 |
| Northern NSW | -28.80 | 153.40 |

These coordinates are regional environmental covariates, not inferred orchard
locations and not fitted biological parameters.

## Provenance and interpretation

The provider is [Open-Meteo](https://open-meteo.com/), using its forecast API
and automatic `best_match` model selection. Each response records the provider,
resolved coordinate, retrieval time and forecast end. Stored mode remains the
required mode for reproducibility checks and retrospective validation.

Live output retains MIFE's existing interpretation: relative population
phenology and pressure, not bugs per tree, an economic threshold or a pesticide
recommendation.
