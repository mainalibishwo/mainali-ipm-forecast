# MIFE v0.1 seasonal reproductive-activation envelope

This file freezes the sensitivity scenarios before comparison with the
21 Malua, Knockrow and Dorey observations.

## Evidence constraint

Waite (2000) reported that ambient egg production by *Amblypelta nitida*
and *A. lutescens* virtually ceased in winter, tracked the shared seasonal
day-length/temperature pattern, and increased after winter. The study did
not experimentally separate photoperiod from temperature.

## Implementation

Temperature remains exclusively in the frozen age-specific fecundity
surface. A separate smooth day-length multiplier represents structural
uncertainty in seasonal reproductive activation. It uses a Northern NSW
regional representative latitude of 28.8°S. This avoids false orchard-level
coordinate precision and changes day length only minimally across the three
nearby orchards.

The preregistered profiles are:

| Profile | Lower day length | Full activation | Winter floor |
|---|---:|---:|---:|
| Conservative | 11.00 h | 12.25 h | 0.000 |
| Central | 10.75 h | 12.00 h | 0.025 |
| Permissive | 10.50 h | 11.75 h | 0.050 |

Between the lower and upper bounds, activation follows a smoothstep curve.
All three profiles must be reported together. None may be selected because
it agrees best with the field-validation observations.

The `reference` profile remains 1.0 throughout the year and preserves the
original MIFE v0.1 output for regression testing.

## Status

These curves are a qualitative uncertainty envelope, not estimated
photoperiod parameters and not evidence of diapause. A future quantitative
fit requires recoverable raw seasonal egg-production data or defensible
digitisation with uncertainty from the independent ambient study.
