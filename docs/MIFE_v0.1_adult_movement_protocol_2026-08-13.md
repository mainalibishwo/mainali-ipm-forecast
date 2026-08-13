# MIFE v0.1 adult movement/immigration sensitivity protocol

## Status

This protocol defines an optional external forcing layer. It does not alter the
frozen MIFE thermal-development, immature-survival, adult-survival, fecundity,
sex-allocation or seasonal reproductive-activation models. The reference case
has exactly zero external entry.

## Independent ecological evidence

Waite (2000) provides direct mark–recapture evidence that fruitspotting bugs can
remain relatively sedentary in attractive hosts while adult immigration and
emigration continue:

- one laboratory-reared *A. lutescens* was observed six weeks after release;
- only one bug crossed between mock-orange clumps approximately 75 m apart;
- recruitment of unmarked adults exceeded that expected from recorded nymphs,
  indicating immigration into favoured hosts;
- most recaptured bugs in papaw remained close to their release trees, with
  only a few moving several rows;
- marked bugs shifted from mock orange to flowering *Bauhinia* as mock-orange
  fruit declined;
- one marked *A. nitida* was recovered about 200 m from its release orchard;
- the report concluded that adjacent host sources, seasonal activity and crop
  susceptibility were more important than long-distance migration.

Waite and Huwer (1998) likewise identify alternative and rainforest hosts as
breeding/refuge sites from which bugs can enter commercial orchards. Danne et
al. (2014) caution that movement into, out of and within crops remains poorly
quantified.

## What the evidence supports

The model may represent adult entry as a local, host-linked external process.
Entrants are adults, are added explicitly, and retain their stated sex and age.
The zero-entry reference remains unchanged.

## What the evidence does not support

The available studies do not estimate a transferable daily immigration rate,
a universal flight-distance distribution, a fixed sex ratio of immigrants, or
a calendar date on which entry begins. They also do not justify deriving entry
from the 21 Malua, Knockrow and Dorey observations.

Consequently MIFE v0.1 must not contain a fitted default immigration rate or a
hard-coded spring pulse. Numerical entry schedules require an independent data
source, such as monitoring in adjacent hosts, orchard-edge surveillance or a
prospectively specified experiment.

## Software boundary

`backend.engine.movement.AdultEntry` is an external forcing record.
`apply_adult_entry` adds independently specified adults after a daily
biological timestep. This ordering prevents entrants from surviving, ageing or
reproducing retrospectively on their entry day. With no entry, the original
simulation state object is returned exactly.

The movement layer is not connected to the public forecast API at this stage.
This prevents an unsupported entry scenario from being presented as an
operational forecast.

## Preregistered future sensitivity axes

When independent entry information becomes available, all scenarios must be
reported, including zero entry. Sensitivity axes are:

1. cumulative number of adult entrants relative to the initialized adult
   population;
2. timing supplied by independent adjacent-host or orchard-edge monitoring;
3. concentrated entry at an orchard edge versus uniform orchard-level entry;
4. entrant sex and physiological-age composition when independently observed;
5. discrete observed entry events versus a diffuse monitoring-derived series.

No axis level may be chosen because it agrees best with the 21 validation
events. Those observations remain evaluation data, not movement calibration
data.

## Sources

- Waite, G.K. (2000). *Ecology and behaviour of fruitspotting bugs*, project
  HG97010, Horticultural Research and Development Corporation.
- Waite, G.K. and Huwer, R.K. (1998). Host plants and their role in the ecology
  of the fruitspotting bugs. *Australian Journal of Entomology* 37:340–349.
- Danne, A.W. et al. (2014). Fruitspotting bugs, *Amblypelta nitida* and
  *A. lutescens lutescens*: a review of integrated management potential.
  *Austral Entomology*.
