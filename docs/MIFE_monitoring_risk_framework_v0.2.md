# MIFE monitoring-risk framework v0.2

## Purpose

This framework translates MIFE outputs into a transparent orchard-monitoring
priority without presenting an unvalidated probability of crop loss. It keeps
three biologically different lines of evidence separate:

1. **Regional population activity** — the weather-driven nymph-plus-adult index,
   its activity band and its 14-day direction.
2. **Crop exposure** — the grower-selected BBCH stage and whether susceptible
   reproductive tissue is present.
3. **Orchard evidence** — optional current live-bug observations and a separate
   nut-injury check.

The framework is implemented in `backend/risk.py`, exposed through
`POST /risk-assessment`, and covered by automated tests. Its rules are therefore
versionable and reproducible.

## Activity bands

The regional index is scaled within each location and displayed season. The
communication bands are:

| Relative activity index | Band |
|---:|---|
| 0 to <10 | Low |
| 10 to <30 | Moderate |
| 30 to <70 | High |
| 70 to 100 | Very high |

These bands describe position within the modelled seasonal activity profile.
They are not bug densities or economic thresholds. A 14-day change greater than
2 index points is labelled increasing, below -2 decreasing, and otherwise
stable.

## Monitoring-priority rules

- High or very-high regional activity overlapping inflorescence, flowering,
  early fruit or nut development produces high or very-high monitoring priority.
- Moderate activity, or a clearly increasing trajectory, during those stages
  produces enhanced monitoring priority.
- High activity during maturation produces enhanced monitoring because visible
  injury can lag exposure.
- A current live FSB/BSB detection increases the priority to at least high
  monitoring while crop is present.
- A non-detection does not cancel a regional signal. Samples of fewer than 20
  trees are explicitly labelled as limited evidence.
- Recorded nut injury is reported with its denominator but does not rescale the
  population forecast or independently trigger treatment, because injury may
  have accumulated before the assessment date.
- Where crop stage is unknown, crop exposure and integrated priority are not
  assessed. Post-harvest output is labelled seasonal surveillance.

## Scientific interpretation

The framework is scientifically defensible as a structured monitoring aid
because it preserves the distinction between pest hazard, crop exposure and
orchard evidence. It does not claim to estimate the probability or economic
severity of damage.

The multi-season validation checkpoint found useful discrimination of confirmed
detection from non-detection (AUC 0.731 across 18 independent events), but the
sample is too small and heterogeneous to fit or validate crop-stage-specific
economic risk thresholds. Most available field validation evidence is for FSB,
while the operational forecast combines FSB and BSB because nymphs are not
reliably separated in routine field observations.

## Requirements for a fitted damage-risk model

A later probability-of-damage model requires prospectively linked observations
with consistent units and dates: live FSB/BSB counts, sampling method and effort,
BBCH stage, cultivar, block identity, weather, management history and subsequent
nut injury or yield loss. Candidate models should be evaluated using
leave-orchard-out and leave-season-out validation, calibration as well as
discrimination, and an independent prospective season before grower release.

Until those requirements are met, the dashboard must use the terms *relative
activity*, *crop exposure* and *monitoring priority*, not economic risk,
probability of damage or treatment threshold.
