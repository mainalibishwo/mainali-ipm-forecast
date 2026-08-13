# MIFE v0.1 Northern NSW field diagnostic

## Scope and guardrails

This diagnostic uses 21 independent Amblypelta field events: seven each from
Malua, Knockrow and Dorey. It reports the complete preregistered seasonal
initialization envelope (three activation profiles by three overwintering-adult
age bands). Starting abundance is fixed at 100 adults for plotting because the
normalized trajectories were already shown to be abundance-invariant.

No thermal-development, survival, fecundity or other frozen biological
parameter was changed. No initialization scenario was selected by field fit.

## Main findings

- Eight of the 21 events were positive for FSB; all BSB observations were zero.
- Five of the eight positive events occurred when the nine-scenario median
  mobile relative-pressure index was below 10/100.
- The early positive events were Malua on 4 September and 5 November,
  Knockrow on 30 July, 8 October and 13 December 2024.
- The Knockrow 13 December event was seven days after an explicitly
  FSB-labelled management event and had a minimum recovered effort of 15
  containers. It is therefore strongly context-dependent.
- Three field events occurred within 21 days of explicitly FSB-labelled
  management: Knockrow on 7 November and 13 December, and Dorey on 10 October.
- Four events had lower recovered sampling effort (15 or fewer containers).
- Field sampling ended in February 2025, whereas the modelled mobile peaks
  occur from late March to late April. The observations therefore do not test
  the predicted annual maximum.
- At the July–September observations, the modelled mobile population is mostly
  overwintering adults. During the later spring and summer observations,
  nymphs dominate the modelled mobile population.

## Interpretation

The field detections broadly show that Amblypelta can be present in orchards
before the closed population trajectories predict substantial relative
pressure. This is scientifically compatible with adult immigration, local
movement among host plants and orchards, or an incompletely represented
overwintering state. The current engine has no immigration term, and the
drop-sheet observations cannot distinguish locally surviving adults from
immigrants.

The result does not isolate a fault in thermal development, survival or
fecundity. Those processes should remain frozen. The present 21 events are too
sparse, management-confounded in places, and temporally truncated before the
predicted peak to support biological recalibration.

## Diagnostic classification

The accompanying event table uses transparent screening flags:

- `management-confounded`: explicitly FSB-labelled management within 21 days;
- `lower recovered sampling effort`: 15 or fewer recovered containers;
- `positive detection during low modelled relative pressure`: positive field
  count when the nine-scenario median normalized mobile index is below 10/100;
- `non-detection during elevated modelled relative pressure`: zero field count
  when the median index is at least 25/100.

The numerical cut-offs are diagnostic display rules, not biological thresholds
and not MIFE parameters.

## Recommended next evidence

The most valuable next field dataset would extend standardized sampling through
March–May, retain FSB and BSB identities, record spray timing and chemistry,
and use a known sampling denominator. Repeated adult and nymph observations at
shorter intervals would help distinguish orchard immigration from local
reproduction. Until then, MIFE v0.1 should be described as a regional
weather-driven phenology and relative-pressure prototype rather than an
absolute orchard abundance forecast.
