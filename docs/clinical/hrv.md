# Heart-rate variability (HRV)

**Columns:** `hrv_sdnn_ms`, `hrv_rmssd_ms`, `hrv_pnn50` · **Units:** ms, ms, % ·
**Measured on:** lead II (default)

**In one sentence:** heart-rate variability describes how much the time between heartbeats
changes from one beat to the next.

!!! example "Everyday picture"
    A healthy heart is **not** a metronome. It speeds up a little every time you breathe in and
    slows down when you breathe out, and it keeps adjusting to what the body needs. A relaxed,
    healthy heart shows more of this wobble; stress, exercise, illness and age reduce it. A heart
    that beats with almost perfect regularity is not a sign of good health.

## Try it

The top strip shows the first 10 seconds with each RR interval written above it. The bottom plot
(a *tachogram*) shows every RR interval of the whole recording. Red links mark beat-to-beat
jumps of more than 50 ms.

<div class="mviz" data-viz="clinical" data-focus="hrv">Interactive demo loading… (needs JavaScript)</div>

What to notice:

- **Relaxed**: the RR intervals swing slowly up and down with breathing.
- **Stressed / exercising**: fast and very regular, so all three numbers drop.
- **Irregular rhythm**: big random jumps between neighbouring beats. RMSSD and pNN50 shoot up.
  Very high values in a short ECG often point to an irregular rhythm such as atrial fibrillation,
  rather than to a "healthy" heart.
- **10-second ECG**: with only about 10 beats the numbers jump around when you change other
  settings. Standard 10 s ECGs give rough HRV estimates.

## The three numbers

| Column | Name | What it captures |
|---|---|---|
| `hrv_sdnn_ms` | SDNN: standard deviation of the RR intervals | the **overall** spread, slow swings included |
| `hrv_rmssd_ms` | RMSSD: root mean square of successive differences | the **typical jump** between neighbouring beats |
| `hrv_pnn50` | pNN50: percentage of successive differences above 50 ms | **how often** neighbouring beats differ noticeably |

There are no single "normal" values. HRV falls with age, rises with fitness, and depends heavily
on the length of the recording, which is why HRV norms are usually given for 5-minute or 24-hour
recordings.

## Why it matters for synthetic ECGs

Many generators learn one "typical" beat and repeat it at a perfectly steady pace. Each beat looks
right, but the rhythm is unnaturally regular, with HRV close to zero. Comparing the HRV
distributions of real and synthetic recordings catches this. The
[`hrv` metric](../metrics/hrv.md) does that comparison automatically.

## How ECGEN-Eval measures it

1. R peaks are detected on the primary lead (the same peaks as [heart rate](heart-rate.md)).
2. RR intervals outside 300–2000 ms are dropped as implausible.
3. From the remaining RR series: SDNN (sample standard deviation), RMSSD and pNN50, with pNN50
   in percent (0–100).

At least three R peaks are needed; otherwise the values are `NaN`.

!!! note "pNN50 units differ"
    The `hrv_pnn50` feature is a percentage (0–100). The [`hrv` metric](../metrics/hrv.md)
    computes pNN50 as a fraction (0–1). Both are fine for comparing real with synthetic data,
    but don't mix them.

## Learn more

- [Heart rate & RR](heart-rate.md) · [HRV metric](../metrics/hrv.md)
- Task Force of the ESC and NASPE (1996). Heart rate variability: standards of measurement,
  physiological interpretation, and clinical use. *Circulation* 93(5), 1043–1065.
  [doi:10.1161/01.CIR.93.5.1043](https://doi.org/10.1161/01.CIR.93.5.1043)
- Shaffer & Ginsberg (2017). An overview of heart rate variability metrics and norms.
  *Frontiers in Public Health* 5, 258. [doi:10.3389/fpubh.2017.00258](https://doi.org/10.3389/fpubh.2017.00258)
