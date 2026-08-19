# MIFE field-adjusted sampling outlook

## Purpose

The grower dashboard updates the regional weather-driven trajectory with a
current, consistently collected tree-based field observation. The output is
expressed as combined FSB/BSB sampling-equivalent bugs/ha. This is a practical
area-standardized planning estimate, not a census of every insect, an economic
threshold or a treatment recommendation.

## Evidence base

The consolidated archive contains 156 orchard/block-date events from 2023–24
to 2025–26. Of 152 events with a usable tree denominator, approximately 66%
had no confirmed or ambiguous FSB/BSB detection. Later project visits usually
sampled four drop-sheet trees. Because field labels include FSB, BSB and
ambiguous `BSB/FSB`, these categories are combined operationally.

The preliminary count-rate relationship was frozen from the 2024–25 Northern
NSW model-linked events before inspecting the 2025–26 out-of-time results. A
Poisson log-link model used count per recovered drop-sheet tree as the response,
recovered trees as weights and `log(1 + regional index)` as the predictor:

`regional bugs/tree = exp(-2.5910446) × (1 + index)^0.14813414`

The dataset is sparse and overdispersed, so this relationship is used only as
a stabilizing regional prior. It must not be interpreted as a precise
population-density conversion.

## Orchard update

The prior is assigned the strength of one four-tree research sample. This is
an internal calibration weight derived from the research protocol, not a
required grower sampling unit. For `y` combined FSB/BSB observed from `n`
sampled trees:

`updated bugs/tree = (4 × regional bugs/tree + y) ÷ (4 + n)`

The local multiplier is the updated current rate divided by the current
regional prior rate. The same multiplier is applied to the regional prior rate
at 7 and 14 days. Consequently:

- a small zero sample lowers but does not eliminate the outlook;
- a positive observation raises the orchard-adjusted outlook;
- a larger sample has more influence than a smaller sample; and
- the regional weather trajectory determines the subsequent direction.

The updated per-tree rates are converted to the grower-facing area unit using:

`trees/ha = 10,000 ÷ (row spacing × within-row spacing)`

`sampling-equivalent bugs/ha = updated bugs/tree × trees/ha`

Growers can enter known tree density directly. Because scouting methods differ
in detection efficiency, non-drop-sheet observations are most informative when
the method and effort are kept consistent across visits. The underlying
calibration used research drop-sheet data; the interface does not imply that
four-tree drop-sheet sampling is normal commercial practice.

## Management and damage boundaries

A recent FSB/BSB-targeted spray is displayed as an interpretation flag. No
efficacy correction is applied because product, coverage, timing and local
response are not sufficiently standardized in the archive.

Nut damage is reported independently using the number damaged and the number
examined. An approximate 95% Wilson interval is displayed. Damage does not
rescale the current insect outlook because injury can pre-date the sample and
cause attribution can be uncertain.

## Required validation

The numerical field-adjusted outlook should be re-estimated and independently
tested when additional standardized observations become available, especially
March–May visits and samples with explicit zero records. Leave-one-orchard and
leave-one-season-out performance should be reported before any action threshold
is considered.
