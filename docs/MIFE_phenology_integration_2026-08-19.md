# MIFE crop-phenology integration decision — 19 August 2026

## Decision

Macadamia BBCH is incorporated as a phenology-informed monitoring layer, not as an unvalidated multiplier of the regional FSB/BSB population.

The regional population engine continues to use weather and frozen spotting-bug development, survival, reproduction and seasonal-activation assumptions. The grower-observed BBCH group is combined with the current regional activity band and trajectory to produce a monitoring priority. Current orchard sampling remains the mechanism that updates the local abundance outlook.

## Evidence audit

The multiseason event inventory contains 156 de-identified orchard/block-date events. Median BBCH is available for 112 events: 82 in 2024–25 and 30 in 2025–26. Target or ambiguous FSB/BSB detections occurred at multiple reproductive BBCH groups.

| BBCH group | Events | Positive events | FSB/BSB or ambiguous individuals |
|---|---:|---:|---:|
| <50 | 4 | 3 | 7 |
| 50–59 | 29 | 11 | 23 |
| 60–69 | 16 | 7 | 18 |
| 70–73 | 12 | 2 | 5 |
| 74–79 | 33 | 9 | 12 |
| 80–89 | 18 | 12 | 27 |

These are descriptive sampling results, not stage-specific population rates. BBCH advances with calendar date and is consequently entangled with accumulated temperature, rainfall, season, region, cultivar, management and sampling effort. The high crude detection proportion at BBCH 80–89, for example, cannot establish that maturation increases abundance; it may reflect later seasonal population build-up or differences among sampled orchards.

## Biological interpretation

Crop phenology can plausibly affect local FSB/BSB occupancy through host-resource availability, tissue suitability and movement among hosts. It does not directly determine physiological development in the same way temperature does. Regional population dynamics and orchard crop exposure are therefore related but distinct processes.

## Model interpretation

Putting a crude BBCH coefficient inside the population engine would:

1. count some seasonal timing twice because both weather and BBCH track date;
2. transfer orchard-level crop observations to a regional population without evidence;
3. imply causality from sparse observational detections;
4. create cultivar and region extrapolation risk; and
5. make the population curve change when a grower changes a decision-support input.

The implemented separation avoids those errors while making phenology operationally useful.

## Rule implemented in the grower dashboard

- Unknown crop stage: monitoring priority is not assessed.
- Post-harvest/senescence: the output is framed as seasonal population surveillance.
- High or very-high regional activity with reproductive tissue present: high or very-high monitoring.
- Moderate or increasing activity with reproductive tissue present: enhanced monitoring.
- Maturation with high regional activity: targeted field confirmation, without assuming maximum crop risk.
- Otherwise: routine monitoring.

These are transparent monitoring categories, not crop-damage probabilities, economic thresholds or pesticide recommendations.

## Requirement for a future abundance modifier

A fitted crop-stage abundance effect should be considered only after repeated orchard/block sampling provides consistent denominators and spans the same BBCH stages under different dates and weather conditions. Candidate models should control for orchard/block, cultivar, season, management, sampling method and effort, and should improve leave-season-out and leave-orchard-out prediction relative to the frozen weather-only model. External validation should precede grower deployment.
