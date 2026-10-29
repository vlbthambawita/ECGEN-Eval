# ST deviation

**Column:** `st_deviation_mv` · **Unit:** mV (in your signal's units) ·
**Measured on:** every lead, then averaged

**In one sentence:** the ST segment is the short flat stretch right after the main spike; ST
deviation is how far it sits above or below the baseline.

!!! example "Everyday picture"
    Right after the main spike the lower chambers are fully activated and holding the squeeze.
    Electrically it is a quiet moment, so the line should rest on the same level as the quiet
    stretch before the beat, like a spirit level that reads flat. If part of the heart muscle is
    short of oxygen, that region does not stay quiet, and the line is lifted or pushed down.

## Try it

<div class="mviz" data-viz="clinical" data-focus="st">Interactive demo loading… (needs JavaScript)</div>

What to notice:

- **The baseline** (dashed) is the flat stretch just before the QRS, not zero volts.
- **The J point** is where the QRS ends and the ST segment begins. The ST level is read a little
  later (80 ms here), once the line has settled.
- **Raised**: a clearly raised ST segment in several leads is one of the signs doctors look for
  in a heart attack. **Lowered** can point to a part of the heart muscle that is short of oxygen.

## What's typical

| ST level vs. baseline | Plain meaning |
|---|---|
| between about −0.05 and +0.1 mV (within 1 small box) | near baseline, typical |
| above +0.1 mV | raised (*ST elevation*) |
| below −0.05 mV | lowered (*ST depression*) |

The exact thresholds depend on the lead, age and sex, and doctors always look at several leads
together.

## Why it matters for synthetic ECGs

ST shifts are subtle (a fraction of a small box) and carry important meaning. A generator that
adds a small offset after every QRS, or lets the baseline drift, turns healthy-looking ECGs into
"ischaemic" ones. If the real data are mostly healthy, the synthetic ST distribution should be
centred near zero too.

## How ECGEN-Eval measures it

For every lead:

1. The **baseline** of each beat is the median level from 40 ms to 10 ms before the QRS onset
   (the flat PR segment).
2. The **ST level** is read 80 ms after the end of the QRS (the J point, found from all leads
   together; see [QRS duration](qrs-duration.md)).
3. ST deviation = ST level − baseline, median over beats. The summary averages the leads.

Works with or without NeuroKit2. Against the Philips Uni-G ST level at J + 80 ms: r 0.97
([validation](index.md#validation)).

## Learn more

- [T-wave amplitude](t-wave.md): measured against the same baseline.
- Rautaharju et al. (2009), AHA/ACCF/HRS recommendations, Part IV.
  [doi:10.1161/CIRCULATIONAHA.108.191096](https://doi.org/10.1161/CIRCULATIONAHA.108.191096)
