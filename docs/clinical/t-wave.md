# T-wave amplitude

**Column:** `t_amplitude_mv` · **Unit:** mV (in your signal's units) ·
**Measured on:** every lead, then averaged

**In one sentence:** the T wave is the rounded bump after the main spike, made by the lower
chambers recharging; its amplitude is how tall that bump is above the baseline.

!!! example "Everyday picture"
    After every pump stroke the lower chambers reset, like a spring winding back up. The T wave
    is that reset. In most leads it is a gentle, upright hill, smaller than the main spike. Its
    height and direction change with the body's salt balance (especially potassium), with the
    oxygen supply to the heart muscle, and with the size of the heart.

## Try it

<div class="mviz" data-viz="clinical" data-focus="t">Interactive demo loading… (needs JavaScript)</div>

What to notice:

- **Typical**: an upright hill that rises slowly and falls a bit faster.
- **Upside down (inverted)**: normal in a few leads (for example aVR), but in most leads doctors
  take note. It can follow reduced blood supply or a thickened heart wall.
- **Tall and peaked**: one classic cause is too much potassium in the blood.
- **Flat**: can follow low potassium or some medicines.

## What's typical

| T-wave height (lead II, rough guide) | Plain meaning |
|---|---|
| below 0 mV | upside down (*inverted*) |
| 0–0.1 mV | flat |
| about 0.1–0.5 mV | typical |
| above 0.5 mV | tall |

T waves are naturally taller in the chest leads (V2–V4), so ranges depend on the lead. ECGEN-Eval
averages over all leads, which is fine for comparing real and synthetic sets measured the same
way.

## Why it matters for synthetic ECGs

The T wave is low and wide, so generators that focus on the sharp QRS may shrink, flatten or
even flip it. Matching the distribution of T heights is a simple check that the model learned
the recharge part of the beat, not just the spike.

## How ECGEN-Eval measures it

For every lead:

1. The **baseline** is the median level between 200 ms and 50 ms before each R peak.
2. The T peak of each beat is found by NeuroKit2's delineation (without NeuroKit2: the highest
   point 100–400 ms after the R peak).
3. `t_amplitude_mv` = mean T-peak level − baseline. The summary averages it over all leads.

## Learn more

- [ST deviation](st-deviation.md) · [QT & QTc](qt-qtc.md)
- Rautaharju et al. (2009), AHA/ACCF/HRS recommendations, Part IV.
  [doi:10.1161/CIRCULATIONAHA.108.191096](https://doi.org/10.1161/CIRCULATIONAHA.108.191096)
