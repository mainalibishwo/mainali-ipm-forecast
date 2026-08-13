# MIFE v0.1 multi-season field-validation checkpoint

Date: 14 August 2026

## Scope and safeguards

Eight field-data workbooks were reviewed to extend validation across the
2023–24, 2024–25 and 2025–26 seasons. The MIFE biological parameters and the
nine preregistered seasonal-initialisation scenarios were not changed.

The raw files remain outside the repository because they contain GPS locations
and personal identifiers. The derived event inventory is de-identified and
contains no scout names or coordinates.

The analysis distinguishes:

- confirmed FSB;
- confirmed BSB;
- ambiguous combined identifications such as `BSB / FSB`; and
- other organisms.

Ambiguous records are never divided between species. A zero in the event
inventory means no target row was recovered in the available sample records; it
does not prove orchard absence. Recovered containers are an observed effort
measure and may be smaller than the planned sampling effort.

## Added evidence

The reproducible extraction created 156 orchard/block-date events:

| Season | NNSW | SEQ | CQ | Total |
|---|---:|---:|---:|---:|
| 2023–24 | 6 | 12 | 26 | 44 |
| 2024–25 | 21 | 15 | 46 | 82 |
| 2025–26 | 18 | 12 | 0 | 30 |
| Total | 45 | 39 | 72 | 156 |

The original 21-event NNSW validation is contained within the 2024–25 files and
must not be counted as new independent evidence. The 18 NNSW events from
2025–26 were therefore reserved as an out-of-time test.

Across those 18 independent events there were five confirmed positive events
and seven confirmed FSB/BSB individuals. Ambiguous records were excluded from
this primary species-confirmed test.

## Frozen-model diagnostic result

Each 2025–26 event was joined to all nine frozen combinations of seasonal
activation profile and overwintering-adult age band. The relative mobile index
was calculated within each scenario, then the median and full scenario range
were retained for every event. Starting abundance was fixed at the reference
value because normalized phenology is abundance-invariant.

Pooled results:

- discrimination of confirmed detection versus non-detection: AUC 0.731;
- Spearman association between confirmed count and median mobile index: 0.345;
- median index at positive events: 9.09;
- median index at non-detection events: 3.55; and
- two events occurred within 21 days of explicitly FSB-labelled management.

These are encouraging diagnostic signals, particularly because the data were
not used to change the model. They are not sufficient to define an economic
threshold, bugs per hectare, or a pesticide action point. There are only five
positive events, site-level estimates are unstable, management is a potential
confounder, and the completed observations end in February 2026. Consequently,
the new data still do not directly test the modelled March–May population peak.

## Geographic use

Queensland records improve the evidence base but should initially be treated as
an external transportability analysis rather than pooled with NNSW. Species
composition, latitude, orchard management and the high frequency of ambiguous
`BSB / FSB` labels differ by region. Weather series matched to each Queensland
orchard or regional site are required before a comparable mechanistic join.

## Dashboard implication

No biological or dashboard forecast adjustment is justified at this checkpoint.
The public wording should continue to describe a relative, weather-driven
phenology forecast. A future evidence-based adjustment would require:

1. sampling through at least May, especially around the forecast peak;
2. consistent species-level identification where feasible;
3. complete planned and recovered sampling effort;
4. management timing retained as a prespecified covariate; and
5. a larger positive-event set for uncertainty intervals and held-out testing.

## Reproduction

Raw workbooks are read-only inputs supplied with `--source-dir`:

```bash
python scripts/build_mife_multiseason_validation.py --source-dir /path/to/raw_workbooks
python scripts/run_mife_multiseason_validation.py
```

Primary outputs are:

- `data/validation/MIFE_v0.1_multiseason_event_inventory.csv`;
- `data/validation/MIFE_v0.1_multiseason_management_deidentified.csv`;
- `data/output/MIFE_v0.1_multiseason_validation_QA.csv`;
- `data/output/MIFE_v0.1_NNSW_2025_26_out_of_time_joined.csv`; and
- `data/output/MIFE_v0.1_NNSW_2025_26_out_of_time_summary.csv`.
