# Peak Signal-to-Noise Ratio (PSNR)

**Key:** `psnr` · **Family:** signal fidelity · **Better:** higher ↑ · **Per-lead:** yes

PSNR asks: *how strong is the signal compared with the error?* It turns the mean squared
error into decibels relative to the real signal's peak-to-peak range, so a value of 30 dB
means the error power is 1000 times smaller than the squared range.

## Try it

<div class="mviz" data-viz="pointwise" data-highlight="psnr">Interactive demo loading… (needs JavaScript)</div>

What to notice:

- Identical beats give **∞ dB** (zero error).
- Every halving of the RMS error adds about **6 dB**. The scale is logarithmic, so the
  first bit of noise costs many decibels and further noise costs fewer.
- **20 ms late** drops PSNR sharply, as with every point-wise metric.

## How it works

1. For each real recording, find the **nearest synthetic recording** (smallest Euclidean
   distance over all leads).
2. Per lead, compute the MSE between the pair and the peak-to-peak range of the real signal.
3. Convert to decibels and average; the score is the mean over leads.

## The math

\[
\mathrm{PSNR} = 10\,\log_{10}\frac{\mathrm{MAX}^2}{\mathrm{MSE}},
\qquad \mathrm{MAX} = \max_t x_r[t] - \min_t x_r[t],
\qquad \mathrm{MSE} = \frac{1}{T}\sum_t (x_r[t]-x_s[t])^2
\]

## Reading the score

- In **dB**, higher is better, unbounded above. Because it is normalised by the signal's own
  range, it is less sensitive to absolute units than MAE.
- A single number on a log scale hides *where* the error is; inspect waveforms too.
- Same caveats as other point-wise metrics: timing and baseline offsets dominate.

## Use it with ECGEN-Eval

=== "CLI"

    ```bash
    ecgen-eval eval --real real.npy --synthetic synth.npy -m psnr --output report.html
    ```

=== "Python"

    ```python
    from ecgen_eval import load_ecg_npy, AVAILABLE_METRICS

    real = load_ecg_npy("real.npy", fs=500)
    synth = load_ecg_npy("synth.npy", fs=500)

    result = AVAILABLE_METRICS["psnr"]().compute(real.data, synth.data, lead_names=real.lead_names)
    print(f"PSNR = {result.score:.1f} dB")
    ```

Parameters are in the [Metric Reference](../user-guide/metric-reference.md#psnr).

## Learn more

- Huynh-Thu & Ghanbari, *Scope of validity of PSNR in image/video quality assessment*,
  Electronics Letters 2008.
