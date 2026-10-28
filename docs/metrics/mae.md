# Mean Absolute Error (MAE)

**Key:** `mae` · **Family:** signal fidelity · **Better:** lower ↓ · **Per-lead:** yes

MAE asks: *on average, how many millivolts apart are a real ECG and its closest synthetic
ECG?* It is the simplest point-wise error and is reported in the signal's own units.
ECGEN-Eval reports RMSE alongside it.

## Try it

<div class="mviz" data-viz="pointwise" data-highlight="mae">Interactive demo loading… (needs JavaScript)</div>

What to notice:

- **Noisy**: MAE and RMSE rise together. With **20 ms late**, RMSE rises faster than MAE,
  because squaring emphasises the few large errors around the R peak.
- **Inverted T wave**: a clinically important change produces only a moderate MAE, because
  the T wave is small compared with the QRS complex.

## How it works

1. For each real recording, find the **nearest synthetic recording** (smallest Euclidean
   distance over all leads).
2. Per lead, compute MAE and RMSE between the pair.
3. Average over recordings; the score is the mean MAE over leads. RMSE is in `extra`.

## The math

\[
\mathrm{MAE} = \frac{1}{T}\sum_{t=1}^{T} \left| x_r[t] - x_s[t] \right|,
\qquad
\mathrm{RMSE} = \sqrt{\frac{1}{T}\sum_{t=1}^{T} \big(x_r[t] - x_s[t]\big)^2}
\]

## Reading the score

- In signal units (usually mV), so values depend on scaling and normalisation. Report the
  units and preprocessing with the number.
- MAE is robust to a few large errors; RMSE is not. A big gap between them points to
  localised errors (for example misplaced R peaks).
- Like all point-wise metrics, MAE punishes timing shifts and baseline offsets that a
  cardiologist would ignore.

## Use it with ECGEN-Eval

=== "CLI"

    ```bash
    ecgen-eval eval --real real.npy --synthetic synth.npy -m mae --output report.html
    ```

=== "Python"

    ```python
    from ecgen_eval import load_ecg_npy, AVAILABLE_METRICS

    real = load_ecg_npy("real.npy", fs=500)
    synth = load_ecg_npy("synth.npy", fs=500)

    result = AVAILABLE_METRICS["mae"]().compute(real.data, synth.data, lead_names=real.lead_names)
    print("MAE:", result.score, "RMSE:", result.extra["rmse"])
    ```

Parameters are in the [Metric Reference](../user-guide/metric-reference.md#mae).

## Learn more

- Related point-wise metrics: [PRD](prd.md), [PSNR](psnr.md), [SSIM](ssim.md); shift-tolerant:
  [DTW](dtw.md).
