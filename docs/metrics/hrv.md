# Heart-Rate Variability (HRV)

**Key:** `hrv` · **Family:** physiological · **Better:** lower ↓ · **Per-lead:** yes ·
**Uses:** `fs`

A healthy heart does not beat like a metronome. Intervals between beats lengthen and shorten
with breathing and nervous-system activity. `hrv` asks: *do synthetic ECGs show the same
amount and kind of beat-to-beat variation as real ECGs?*

## Try it

Top: the tachogram (RR interval of each beat over time) of one real and one synthetic
recording. Bottom: the distributions of three HRV statistics over 200 recordings each.

<div class="mviz" data-viz="hrv">Interactive demo loading… (needs JavaScript)</div>

What to notice:

- **Metronome**: a generator that copies one beat at a fixed interval has almost zero SDNN
  and RMSSD, which is easy to spot here even when the heart rate is right.
- **Erratic**: random beat-to-beat jumps inflate RMSSD and pNN50 much more than SDNN.
- **2-minute strips**: with longer recordings the histograms become narrower and the
  statistics more reliable. On 10-second strips (about 12 beats) HRV statistics are very
  noisy.

## How it works

For each lead:

1. Detect R peaks with the slope-energy QRS detector described on the
   [Heart rate](heart_rate.md) page, and compute the RR intervals.
2. Per recording, compute **SDNN**, **RMSSD** and **pNN50**.
3. For each statistic, compare the real and synthetic distributions with the Jensen–Shannon
   divergence (50-bin histograms).
4. The lead's score is the mean of the three divergences; the overall score is the mean over
   leads.

## The math

With RR intervals \(RR_1..RR_N\) in ms:

\[
\mathrm{SDNN} = \sqrt{\frac{1}{N-1}\sum_{i=1}^{N}(RR_i - \overline{RR})^2},
\qquad
\mathrm{RMSSD} = \sqrt{\frac{1}{N-1}\sum_{i=2}^{N}(RR_i - RR_{i-1})^2},
\qquad
\mathrm{pNN50} = \frac{\#\{i : |RR_i - RR_{i-1}| > 50\,\mathrm{ms}\}}{N-1}
\]

\[
\text{score} = \tfrac13\left[\mathrm{JS}_{\mathrm{SDNN}} + \mathrm{JS}_{\mathrm{RMSSD}} + \mathrm{JS}_{\mathrm{pNN50}}\right]
\]

SDNN captures overall variability; RMSSD and pNN50 capture fast, beat-to-beat changes.
ECGEN-Eval reports pNN50 as a fraction (0–1), not a percentage.

## Reading the score

- Range [0, ln 2]. Look at the means in `extra` (`real_sdnn_mean`, `synth_sdnn_mean`, …) to
  see the *direction* of the difference: too regular or too erratic.
- Short-term HRV norms assume at least 5 minutes of recording. On 10 s strips, compare only
  real and synthetic sets of the **same length**, and expect noisy scores.
- Missed or extra R peaks distort HRV heavily; check R-peak detection on noisy data.

## Use it with ECGEN-Eval

=== "CLI"

    ```bash
    ecgen-eval eval --real real.npy --synthetic synth.npy -m hrv --fs 500 --output report.html
    ```

=== "Python"

    ```python
    from ecgen_eval import load_ecg_npy, AVAILABLE_METRICS

    real = load_ecg_npy("real.npy", fs=500)
    synth = load_ecg_npy("synth.npy", fs=500)

    hrv = AVAILABLE_METRICS["hrv"](fs=real.fs)
    result = hrv.compute(real.data, synth.data, lead_names=real.lead_names)
    print(result.score)
    print(result.extra["II"])   # real/synth SDNN, RMSSD, pNN50 means for lead II
    ```

Parameters are in the [Metric Reference](../user-guide/metric-reference.md#hrv).

## Learn more

- Task Force of the ESC and NASPE, *Heart rate variability: standards of measurement,
  physiological interpretation and clinical use*, Circulation 1996.
