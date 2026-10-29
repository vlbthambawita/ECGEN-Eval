# Heart rate & RR interval

**Columns:** `hr_bpm`, `rr_mean_ms`, `rr_std_ms` · **Units:** beats per minute, ms ·
**Measured on:** lead II (default)

**In one sentence:** the RR interval is the time from one heartbeat's main spike (the **R
peak**) to the next one, and the heart rate is how many of those fit into a minute.

!!! example "Everyday picture"
    Think of a drummer keeping time. The RR interval is the gap between two drum hits; the heart
    rate is the tempo. Half the gap means double the tempo.

## Try it

Move the slider and watch the gap between the spikes. The bracket measures one RR interval, and
the bar underneath shows where the rate falls.

<div class="mviz" data-viz="clinical" data-focus="hr">Interactive demo loading… (needs JavaScript)</div>

What to notice:

- **RR and heart rate move in opposite directions.** `hr_bpm` = 60 000 ÷ `rr_mean_ms`, so a
  1000 ms gap is 60 bpm and a 500 ms gap is 120 bpm.
- **The heartbeat itself barely changes shape**; at a fast rate it is the *rest* between beats
  that shrinks.
- **The quick rule doctors use:** count the big boxes between two R peaks and divide 300 by it.
  Four big boxes → 75 bpm.

## What's typical

| Heart rate | Plain meaning | Common everyday reasons |
|---|---|---|
| below 60 bpm (*bradycardia*) | slow | sleep, very fit athletes, some medicines |
| 60–100 bpm | typical at rest | — |
| above 100 bpm (*tachycardia*) | fast | exercise, stress, fever, caffeine |

Neither slow nor fast is automatically a problem; it depends on the person and the situation.
`rr_std_ms` is the spread of the RR intervals within one recording. It is large when the rhythm
is irregular (see [heart-rate variability](hrv.md)).

## Why it matters for synthetic ECGs

Heart rate is the first thing anyone reads off an ECG. A generator should reproduce the **whole
spread** of rates in the real data: not only the average, but also the slow and fast
recordings. A model that produces every ECG at 72 bpm has the right average and still fails.
The [`heart_rate` metric](../metrics/heart_rate.md) compares exactly these distributions.

## How ECGEN-Eval measures it

1. R peaks are detected on the primary lead with NeuroKit2's `ecg_peaks()` (a SciPy
   Pan–Tompkins detector without NeuroKit2).
2. `rr_mean_ms` and `rr_std_ms` are the mean and standard deviation of the gaps between
   consecutive R peaks.
3. `hr_bpm` = 60 000 ÷ `rr_mean_ms`.

Against the GE 12SL heart rate of 60 PTB-XL recordings the mean error is 1.5 bpm. At least two
R peaks are needed; otherwise the value is `NaN`.

## Learn more

- [Heart-rate variability](hrv.md): how much the RR interval changes from beat to beat.
- [QT & QTc](qt-qtc.md): why other timings must be corrected for heart rate.
- Pan & Tompkins (1985), *A real-time QRS detection algorithm*, IEEE TBME.
  [doi:10.1109/TBME.1985.325532](https://doi.org/10.1109/TBME.1985.325532)
