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

For every beat, `pr_interval_ms` is the time from P-wave onset to QRS onset; the recording
value is the median over beats.

- **QRS onset** comes from all leads together: where the combined slope of the leads rises
  above 4 % of its range before the R peak.
- **P onset** comes from NeuroKit2's peak-prominence delineator on every lead (the median
  across leads), refined to where the P wave reaches 15 % of its height.

Needs NeuroKit2 (`NaN` without it). Against GE 12SL: typical error 8.5 ms, r 0.87
([validation](index.md#validation)).

??? info "With other backends"
    - **`neurokit2`**: P onset and QRS onset (`ECG_R_Onsets`) from `nk.ecg_delineate` on the
      primary lead. With `dwt` the QRS onset is searched between the P peak and the Q wave, so
      a misplaced P peak also moves the QRS onset; typical error 52 ms on PTB-XL. `peak` gives
      no QRS onset (`NaN`).
    - **`biosppy`**: P onset and Q start from local extrema of the beat template. The P onset
      lands close to the P peak, so PR is about 37 ms short.
    - **`scipy`**, **`heartpy`**: not measured (`NaN`).

    Details: [How the Extraction Backends Work](../user-guide/feature-backends.md).

## Learn more

- [P-wave duration](p-wave.md) · [QRS duration](qrs-duration.md)
- Kligfield et al. (2007), AHA/ACC/HRS *Recommendations for the standardization and interpretation of the
  electrocardiogram*, Part I. [doi:10.1161/CIRCULATIONAHA.106.180200](https://doi.org/10.1161/CIRCULATIONAHA.106.180200)
