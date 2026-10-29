# Clinical Features Explained

ECGEN-Eval can measure ten **clinical features** on every ECG: the same timings and heights a
cardiologist looks at first. This section explains them for readers **without a medical
background**, with interactive pictures instead of jargon.

!!! info "Educational material, not medical advice"
    The heartbeats here are simplified drawings. The "typical" ranges are rough guides for
    resting adults; real cut-offs vary with age, sex, the lead and the guideline. Use them to
    understand synthetic ECGs, not to read anyone's medical ECG.

## What an ECG is

Every heartbeat is started by a tiny **electrical wave** that travels through the heart muscle,
a little like a stadium wave travelling around a crowd. Muscle squeezes when the wave reaches
it. Electrodes on the skin pick up this wave, and the ECG draws it as a line over time:

- **Left to right is time.** On standard ECG paper, 1 small box = 40 ms (0.04 s) and 1 big box
  (5 small boxes) = 0.2 s. Five big boxes are one second.
- **Up and down is voltage.** 1 small box = 0.1 mV, so 10 small boxes = 1 mV.
- **Flat means nothing is changing**, not that the heart is "off".

Each heartbeat leaves the same pattern of bumps, named with letters: **P, Q, R, S, T**. The
features below are the widths, gaps and heights of those bumps, and the time between beats.

## Anatomy of one heartbeat

Press **Play** to watch the electrical wave travel through the heart while the ECG is drawn.
You can also click any part of the trace or use the buttons. The heart on the right shows which
part of the heart is active at that moment.

<div class="mviz" data-viz="beatAnatomy">Interactive heartbeat loading… (needs JavaScript)</div>

In short:

| ECG part | What the heart is doing | Plain-language picture |
|---|---|---|
| **P wave** | Upper chambers (atria) are activated | The "starter" squeeze that tops up the lower chambers |
| **PR segment** | Signal waits at the AV node | A gate that pauses the signal so the lower chambers can fill |
| **QRS complex** | Lower chambers (ventricles) are activated | The main pump stroke; the biggest spike |
| **ST segment** | Ventricles fully activated | A quiet moment, should be on the baseline |
| **T wave** | Ventricles recharge | Resetting, ready for the next beat |
| **Rest** | Heart relaxes and refills | The pause before the next beat |

## The features

<div class="grid cards" markdown>

-   :material-heart-pulse: **[Heart rate & RR interval](heart-rate.md)**

    ---

    How fast the heart beats, and the time from one beat to the next.

    `hr_bpm` · `rr_mean_ms` · `rr_std_ms`

-   :material-wave: **[P-wave duration](p-wave.md)**

    ---

    How long the upper chambers take to activate.

    `p_wave_duration_ms`

-   :material-timer-sand: **[PR interval](pr-interval.md)**

    ---

    How long the signal takes to get from the upper to the lower chambers.

    `pr_interval_ms`

-   :material-flash: **[QRS duration](qrs-duration.md)**

    ---

    How quickly the electrical wave spreads through the lower chambers.

    `qrs_duration_ms`

-   :material-timer-outline: **[QT interval & QTc](qt-qtc.md)**

    ---

    How long the lower chambers take to activate and recharge, corrected for heart rate.

    `qt_interval_ms` · `qtc_bazett_ms`

-   :material-arrow-up-down: **[ST deviation](st-deviation.md)**

    ---

    Whether the quiet stretch after the main spike sits on the baseline.

    `st_deviation_mv`

-   :material-chart-bell-curve: **[T-wave amplitude](t-wave.md)**

    ---

    How tall the recharge bump is, and whether it points up.

    `t_amplitude_mv`

-   :material-chart-timeline-variant: **[Heart-rate variability](hrv.md)**

    ---

    How much the time between beats changes from beat to beat.

    `hrv_sdnn_ms` · `hrv_rmssd_ms` · `hrv_pnn50`

</div>

| Feature | Column | Unit | Typical resting adult (rough guide) |
|---|---|---|---|
| [Heart rate](heart-rate.md) | `hr_bpm` | beats per minute | 60–100 bpm |
| [RR interval](heart-rate.md) | `rr_mean_ms`, `rr_std_ms` | ms | 600–1000 ms |
| [P-wave duration](p-wave.md) | `p_wave_duration_ms` | ms | up to 120 ms |
| [PR interval](pr-interval.md) | `pr_interval_ms` | ms | 120–200 ms |
| [QRS duration](qrs-duration.md) | `qrs_duration_ms` | ms | under 110–120 ms |
| [QT interval](qt-qtc.md) | `qt_interval_ms` | ms | depends on heart rate |
| [QTc (Bazett)](qt-qtc.md) | `qtc_bazett_ms` | ms | about 350–450 ms |
| [ST deviation](st-deviation.md) | `st_deviation_mv` | mV | close to 0 |
| [T-wave amplitude](t-wave.md) | `t_amplitude_mv` | mV | positive in most leads |
| [HRV](hrv.md) | `hrv_sdnn_ms`, `hrv_rmssd_ms`, `hrv_pnn50` | ms, ms, % | depends strongly on age and recording length |

## Why they matter for synthetic ECGs

A generator can learn to draw something that *looks* like an ECG at a glance but breaks the
rules of how a heart works: a P wave glued to the QRS, a QRS twice as wide as any real one, a
T wave that never ends. Signal-level metrics such as [MMD](../metrics/mmd.md) or
[FED](../metrics/fed.md) may miss this. A cardiologist would spot it in seconds.

Clinical features check exactly these rules. The question is not "is every value normal?"
(real datasets contain disease), but **"do the synthetic features follow the same distribution as
the real ones?"** If 10 % of real ECGs have a wide QRS, about 10 % of synthetic ones should too.

## Use it with ECGEN-Eval

=== "CLI"

    ```bash
    pip install "ecgen-eval[features]"   # adds NeuroKit2 for wave delineation

    # One CSV row per recording, with a `dataset` column
    ecgen-eval features --real real.npy --synthetic synth.npy --fs 500 --output features.csv

    # Or add 2-D / 3-D feature plots to the HTML report
    ecgen-eval eval --real real.npy --synthetic synth.npy --feature-plots --output report.html
    ```

=== "Python"

    ```python
    from ecgen_eval import load_ecg_npy
    from ecgen_eval.features import extract_features

    real = load_ecg_npy("real.npy", fs=500)
    synth = load_ecg_npy("synth.npy", fs=500)

    _, real_summary = extract_features(real)    # one row per recording
    _, synth_summary = extract_features(synth)

    cols = ["hr_bpm", "pr_interval_ms", "qrs_duration_ms", "qtc_bazett_ms"]
    print(real_summary[cols].describe().round(1))
    print(synth_summary[cols].describe().round(1))
    ```

Beats are found on one lead (lead II by default, see `lead_for_intervals`); the wave boundaries
use all leads, and the ST and T heights are measured on every lead and averaged. The [Clinical Features](../user-guide/features.md)
user guide covers the options and output tables. The [ECG Feature Review](../ecg_features_review.md)
gives the clinical background and references.

## How well the measurements agree with clinical software { #validation }

The extractor was compared with the **GE 12SL** measurements that PTB-XL+ publishes for every
PTB-XL recording. The check used 500 recordings from PTB-XL fold 9 (12 leads, 500 Hz, 10 s),
which were not used to tune the extractor. For context, the last column shows how well two
commercial programs, GE 12SL and Philips Uni-G, agree with *each other* on the same kind of
data. P-wave boundaries are hard to pin down even for them.

| Feature | Ours vs 12SL: mean difference | typical error (MAE) | correlation r | 12SL vs Uni-G (r) |
|---|---|---|---|---|
| `hr_bpm` | −0.4 bpm | 1.7 bpm | 0.90 | — |
| `pr_interval_ms` | +2 ms | 8.5 ms | 0.87 | 0.89 |
| `qrs_duration_ms` | +1 ms | 6.4 ms | 0.88 | 0.88 |
| `qt_interval_ms` | −17 ms | 22.6 ms | 0.85 | 0.96 |
| `qtc_bazett_ms` | −17 ms | 25.5 ms | 0.63 | 0.81 |
| `p_wave_duration_ms` | −4 ms | 12.0 ms | 0.41 | 0.48 |
| `t_amplitude_mv` (lead average) | +0.01 mV | | 0.96 | |
| `st_deviation_mv` (lead average, vs Uni-G at J + 80 ms) | 0.00 mV | | 0.97 | |

How to read it:

- **Heart rate, PR, QRS, T amplitude and ST** match the clinical software about as closely as
  the two commercial programs match each other.
- **QT** follows 12SL closely (r 0.85) but is about 17 ms shorter on average: the tangent
  method used for the end of the T wave is known to end it earlier. **QTc** inherits this, and
  it also adds the small errors of QT and RR together, so its correlation is lower.
- **P-wave duration** is the least reliable feature for every algorithm, including the
  commercial ones.
- Accuracy drops with **fewer leads** (single-lead QRS r ≈ 0.5) and **lower sampling rates**
  (at 100 Hz, PR r 0.93 but QRS MAE 13 ms and QT r 0.73).
- **Without NeuroKit2**, heart rate, HRV, QRS duration, ST and T amplitude are still measured;
  PR, QT, QTc and P-wave duration are `NaN`.

Because real and synthetic data go through exactly the same extractor, small systematic
offsets such as the QT bias cancel out when you compare their distributions.

!!! note "Changed in v0.7.0"
    In v0.6.0 and earlier, PR, QT, QTc, P-wave duration and ST deviation were always `NaN`
    with NeuroKit2 installed (and fixed placeholder values without it), and QRS was measured
    from the Q dip to the S dip. Re-extract features made with those versions before
    comparing them with new results.
