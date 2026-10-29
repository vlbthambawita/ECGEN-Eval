# QRS duration

**Column:** `qrs_duration_ms` · **Unit:** ms · **Measured on:** lead II (default)

**In one sentence:** the QRS complex is the big spike of each beat, made by the two lower
chambers (the **ventricles**) activating; its duration is how quickly the electrical wave
spreads through them.

!!! example "Everyday picture"
    The lower chambers have their own fast wiring, like an express train line, that delivers the
    signal to every part of the muscle almost at once. If part of that line is blocked, the
    signal has to crawl through ordinary muscle instead, like taking the slow local roads, and
    the QRS gets wider.

## Try it

<div class="mviz" data-viz="clinical" data-focus="qrs">Interactive demo loading… (needs JavaScript)</div>

What to notice:

- **A typical QRS is narrow**, less than 3 small boxes. It is the fastest part of the beat.
- **Wide (bundle branch block)**: one of the two main wires to the lower chambers is blocked.
  In real ECGs the spike then also changes shape (for example notched "M" shapes in some leads);
  this simple drawing only shows the widening.

## What's typical

| QRS duration | Plain meaning |
|---|---|
| under 110 ms | typical: the fast wiring works |
| 110–120 ms | borderline |
| 120 ms or more (3 small boxes) | wide: the signal spreads slowly, e.g. a *bundle branch block* |

## Why it matters for synthetic ECGs

A narrow, sharp QRS needs a lot of detail in a short time, and generators that blur the signal
tend to make it too wide or too rounded. A synthetic set whose QRS widths are systematically
larger than the real ones looks "diseased" to a clinician even if the overall shape is right.

## How ECGEN-Eval measures it

`qrs_duration_ms` is meant to be the mean time from QRS onset to QRS end over all beats, using
NeuroKit2's wave delineation on the primary lead.

!!! warning "Not yet the clinical QRS width"
    In v0.6.0 the value is measured from the Q dip to the S dip. That is shorter than the full
    QRS and does not correlate with the GE 12SL QRS duration. Without NeuroKit2 it is a fixed
    placeholder. See [Known limitations](index.md#known-limitations).

## Learn more

- [Signal Quality Index](../metrics/sqi.md) and [DTW](../metrics/dtw.md) also react to QRS
  shape.
- Surawicz et al. (2009), AHA/ACCF/HRS recommendations, Part III: intraventricular conduction
  disturbances. [doi:10.1161/CIRCULATIONAHA.108.191095](https://doi.org/10.1161/CIRCULATIONAHA.108.191095)
