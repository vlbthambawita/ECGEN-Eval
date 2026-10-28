# Heart-rate distribution

**Key:** `heart_rate` · **Family:** physiological · **Better:** lower ↓ · **Per-lead:** yes ·
**Uses:** `fs`

`heart_rate` asks: *do the synthetic ECGs beat at the same rates as the real ones?* It
detects R peaks in every recording, converts the RR intervals to a heart rate, and compares
the real and synthetic heart-rate distributions.

## Try it

Top: an example synthetic strip with the R peaks the detector finds (the same detector as
ECGEN-Eval). Bottom: heart-rate
histograms of 300 real and 300 synthetic recordings.

<div class="mviz" data-viz="heartRate">Interactive demo loading… (needs JavaScript)</div>

What to notice:

- **Too fast** shifts the histogram; the divergence rises quickly once they stop overlapping.
- **Tachycardia (150 bpm)**: the detector still finds every beat. Its 0.2 s refractory
  period allows rates up to 300 bpm.
- **Too uniform**: the right mean heart rate is not enough. A generator that always produces
  72 bpm misses the real variety between patients.

## How it works

For each lead:

1. Detect R peaks with a slope-energy QRS detector (in the spirit of Pan & Tompkins):
    - band-pass the signal to 5–15 Hz, which keeps the steep QRS slopes and suppresses
      P and T waves, baseline wander and high-frequency noise;
    - square the derivative and average it over 120 ms, giving a "QRS energy" signal;
    - take energy peaks above 0.2 × its 99th percentile, at least 0.2 s apart (up to 300 bpm);
    - move each detection to the largest absolute band-passed sample nearby, so inverted
      QRS complexes (aVR) are found too.
2. Heart rate per recording = 60 / mean RR interval.
3. Histogram real and synthetic heart rates with 50 bins over their joint range.
4. Compute the Jensen–Shannon divergence between the histograms.

The score is the mean over leads.

## The math

\[
\mathrm{HR} = \frac{60}{\overline{RR}}\ \text{bpm},
\qquad
\text{score} = \mathrm{JS}\big(\mathrm{hist}(\mathrm{HR}^{r}),\ \mathrm{hist}(\mathrm{HR}^{s})\big)
\in [0, \ln 2]
\]

## Reading the score

- 0 means identical heart-rate distributions. Also check the means and standard deviations
  in `extra` (`real_hr_mean`, `synth_hr_mean`, …), which are easier to interpret.
- R-peak detection runs on each lead. On PTB-XL it matches the reference heart rate within
  5 bpm in about 91 % of lead recordings; limb leads III and aVF with small QRS complexes are
  the least reliable, so per-lead scores vary.
- An amplitude threshold on the raw signal (used in ECGEN-Eval 0.5 and earlier) confuses tall T waves with R
  peaks. The slope-based detector avoids this, which allows the short refractory period
  needed for tachycardia.
- For a clinically detailed comparison (PR, QRS, QT intervals and more) use
  [Clinical Features](../user-guide/features.md).

## Use it with ECGEN-Eval

=== "CLI"

    ```bash
    ecgen-eval eval --real real.npy --synthetic synth.npy -m heart_rate --fs 500 --output report.html
    ```

=== "Python"

    ```python
    from ecgen_eval import load_ecg_npy, AVAILABLE_METRICS

    real = load_ecg_npy("real.npy", fs=500)
    synth = load_ecg_npy("synth.npy", fs=500)

    hr = AVAILABLE_METRICS["heart_rate"](fs=real.fs)
    result = hr.compute(real.data, synth.data, lead_names=real.lead_names)
    print(result.score, result.extra["II"])   # real/synth HR mean and std for lead II
    ```

Parameters are in the [Metric Reference](../user-guide/metric-reference.md#heart_rate).

## Learn more

- Pan & Tompkins, *A Real-Time QRS Detection Algorithm*, IEEE TBME 1985.
- [Heart-Rate Variability](hrv.md) looks at how the beat timing varies within a recording.
