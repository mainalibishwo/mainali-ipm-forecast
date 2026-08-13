# MIFE autumn peak: evidence and validation decision

## Question

MIFE v0.1 produces a late-March to early-April mobile-population peak in the
Northern NSW validation weather series. This overlaps the beginning of the
macadamia harvest period. Does that timing require adjustment of the frozen
biological parameters?

## Evidence assessment

The available evidence makes an autumn peak biologically plausible:

- NSW macadamia guidance describes 3–4 generations annually: spring, one or
  two summer generations and an autumn generation. Adults from the autumn
  generation survive winter.
- The NSW macadamia plant protection guide states that fruitspotting bug
  populations are still observed as late as April.
- Australian macadamia harvest broadly runs from March into winter. Therefore,
  temporal overlap between an autumn insect generation and harvest is expected
  and is not evidence of model error.
- Crop susceptibility changes through the season. Young-nut attack can produce
  conspicuous nut fall, whereas post-shell-hardening damage can remain in the
  canopy and be detected later as kernel damage. Population phenology, harvest
  activity and crop-damage risk are therefore different quantities.
- Amblypelta movement among crop and non-crop hosts remains poorly quantified.
  A closed population model cannot reproduce immigration-driven orchard
  detections without a separately validated movement component.

Key sources:

1. Bright J. *Fruit spotting bug in macadamia*. NSW Department of Primary
   Industries.
2. Bright J. *Macadamia plant protection guide 2018–19*. NSW DPI and industry
   partners.
3. Ellis KL et al. 2023. Biology and ecology of insect pests in macadamia.
   *Journal of Integrated Pest Management* 14:26.
4. Australian Macadamia Society. *Growing and processing macadamias*.

## Current field-evidence limitation

The 21-event Malua, Knockrow and Dorey dataset ends in February 2025. It does
not observe the predicted March–April maximum. Several observations are also
management-confounded or have lower recovered sampling effort. Consequently,
the dataset cannot validate or reject the autumn peak date or magnitude.

## Adjustment decision

**No biological-parameter adjustment is justified at this checkpoint.**

The literature supports an autumn generation and April field presence. It does
not supply a sufficiently resolved regional abundance curve against which to
shift or scale MIFE's peak. Altering thermal development, survival, fecundity or
seasonal activation now would amount to fitting beyond the evidence.

The peak must be labelled **modelled autumn population peak**, not validated
absolute orchard abundance and not the time of maximum economic damage.

## March–May validation requirement

For each of Malua, Knockrow and Dorey, sample at least fortnightly from 1 March
to 31 May, preferably weekly during the predicted peak window. Record:

- date and orchard/block;
- total trees sampled and one standardized sampling unit per tree;
- FSB and BSB separately, including nymph/adult stage where possible;
- row spacing, within-row tree spacing and/or verified trees per hectare;
- crop stage, nut maturity and shell-hardening status;
- fresh nut-drop damage and retained-nut/kernel damage where assessable;
- insecticide date, active ingredient and target;
- block-edge or interior position and proximity to likely non-crop hosts;
- sampling-equivalent bugs per 100 trees and per hectare.

### Decision rule after new data

1. First test peak timing against the complete nine-scenario envelope; do not
   select a scenario retrospectively merely because it fits best.
2. Treat abundance and timing separately. A consistent timing displacement
   across sites and years is required before considering phenology adjustment.
3. Investigate sampling, management and immigration explanations before any
   biological change.
4. Adjust a frozen biological parameter only when replicated data identify the
   same directional mismatch and independent literature supports the affected
   biological process.
5. Preregister any proposed recalibration and validate it on data withheld from
   fitting.

Until those conditions are met, the frozen MIFE v0.1 biological parameters and
the nine-scenario uncertainty envelope remain unchanged.
