# PR interval

**Column:** `pr_interval_ms` · **Unit:** ms · **Measured on:** lead II (default)

**In one sentence:** the PR interval is the time from the start of the P wave to the start of
the main spike, which is how long the signal takes to travel from the upper to the lower chambers.

!!! example "Everyday picture"
    Between the upper and lower chambers sits a gate, the **AV node**. It deliberately holds the
    signal back for a moment so the lower chambers can finish filling with blood. The PR interval
    is the time from "upper chambers start" to "lower chambers start", and most of it is that
    wait at the gate.

## Try it

<div class="mviz" data-viz="clinical" data-focus="pr">Interactive demo loading… (needs JavaScript)</div>

What to notice:

- **The flat stretch between the P wave and the QRS** grows and shrinks; the P wave and the QRS
  keep their shape.
- **Long (first-degree AV block)**: the gate is slow, but every signal still gets through.
  On its own this is often harmless.
- **Short**: the signal reaches the lower chambers early, sometimes through an extra electrical
  pathway that bypasses the gate.

## What's typical

| PR interval | Plain meaning |
|---|---|
| under 120 ms (3 small boxes) | short: the signal reaches the lower chambers early |
| 120–200 ms (3–5 small boxes) | typical |
| over 200 ms (5 small boxes) | long: the gate is slow (*first-degree AV block*) |

## Why it matters for synthetic ECGs

The PR interval links two separate events (P and QRS) with a fixed rule. A generator that
learned the shapes of the waves but not the timing between them shows up here as PR intervals
that are too short, too long or far too variable.

## How ECGEN-Eval measures it

`pr_interval_ms` is the mean time from P-wave onset to QRS onset over all beats, using
NeuroKit2's wave delineation on the primary lead.

!!! warning "Currently unavailable"
    This feature is always `NaN` in v0.6.0 with NeuroKit2 installed, and a fixed placeholder
    without it. See [Known limitations](index.md#known-limitations).

## Learn more

- [P-wave duration](p-wave.md) · [QRS duration](qrs-duration.md)
- Kligfield et al. (2007), AHA/ACC/HRS *Recommendations for the standardization and interpretation of the
  electrocardiogram*, Part I. [doi:10.1161/CIRCULATIONAHA.106.180200](https://doi.org/10.1161/CIRCULATIONAHA.106.180200)
