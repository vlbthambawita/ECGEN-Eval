# Mean Squared Error and RMSE

**Keys:** `mse`, `rmse` · **Family:** signal fidelity · **Better:** lower ↓ · **Per-lead:** yes

MSE asks: *how far apart, on average and squared, are a real ECG and its matched synthetic
ECG at every sample?* RMSE is its square root, which brings the number back to the signal's
own units (mV). RMSE is the most widely reported quantitative fidelity metric in the
[literature review](../literature/database.md#metrics/Fidelity) (55 papers); MSE follows with 30.

## Try it

<div class="mviz" data-viz="pointwise" data-highlight="mse">Interactive demo loading… (needs JavaScript)</div>

What to notice:

- **Noisy**: MSE grows with the square of the noise level, RMSE linearly.
- **20 ms late**: a shift a cardiologist would ignore gives a large error, because the steep
  QRS complex no longer overlaps. Pearson and cosine drop for the same reason.
- **Baseline drift**: a constant offset `c` adds exactly `c²` to the MSE while Pearson stays
  at 1.
- **Inverted T wave**: a clinically important change gives a *smaller* error than the 20 ms
  shift. The size of a point-wise error says little about clinical relevance.

## How it works

1. Per lead, optionally normalise every recording (`normalize="zscore"` or `"minmax"`).
2. Match real and synthetic signals according to `pairing` (default: nearest neighbour).
3. Compute the MSE of every pair; RMSE is the square root of each pair's MSE.
4. Average over pairs, then over leads.

!!! info "Pairing: which synthetic signal is each real signal compared with?"
    | `pairing` | Compared signals | Use it for |
    |---|---|---|
    | `"nn"` (default) | each real signal and its **nearest** synthetic signal of the same lead | unconditional or class-conditional generation, where no synthetic ECG belongs to a particular real one |
    | `"paired"` | real signal *i* and synthetic signal *i* | reconstruction, lead synthesis, PPG-to-ECG translation |
    | `"mean"` | the mean real waveform and the mean synthetic waveform | beat-aligned data (average beats) |

    Papers report this metric under all three protocols and the numbers are **not comparable**
    between them. State the pairing with the score. See
    [Matching protocol](../user-guide/metric-reference.md#matching-protocol).

## The math

\[
\mathrm{MSE} = \frac{1}{T}\sum_{t=1}^{T} \big(x_r[t] - x_s[t]\big)^2,
\qquad
\mathrm{RMSE} = \sqrt{\mathrm{MSE}}
\]

RMSE is averaged per pair (the mean of the roots, not the root of the mean), so
`rmse` is not exactly \(\sqrt{\texttt{mse}}\).

## Reading the score

- MSE is in squared signal units (mV²) and RMSE in signal units (mV). Both depend on scaling
  and normalisation, so report the units and preprocessing with the number.
- `extra["real_vs_real"]` holds the same statistic between two disjoint halves of the real
  set. Read the score against it: with nearest-neighbour pairing, real data does not score 0 against itself
  either.
- `extra["nrmse"]` (for `rmse`) divides by the peak-to-peak range of the real signal and
  makes leads with different amplitudes comparable.
- A low error can be a bad sign. An over-smoothed generator that outputs "average" beats gets
  a low MSE ([P116](../literature/database.md#papers/P116) observed this for TimeVAE), and so does a generator that copies its
  training data ([P171](../literature/database.md#papers/P171)). Check [`pr_dist`](pr_dist.md) and [`nn_dist`](nn_dist.md)
  alongside.
- Like all point-wise metrics, MSE punishes small timing shifts. Use [`dtw`](dtw.md) when
  timing should be forgiven.

`mse`, `rmse` and [`euclidean`](euclidean.md) are monotone transforms of each other for one
pair. Report the one your comparison papers use; there is no reason to report all three.

## Use it with ECGEN-Eval

=== "CLI"

    ```bash
    ecgen-eval eval --real real.npy --synthetic synth.npy -m mse -m rmse --output report.html
    ```

=== "Python"

    ```python
    from ecgen_eval import load_ecg_npy, AVAILABLE_METRICS

    real = load_ecg_npy("real.npy", fs=500)
    synth = load_ecg_npy("synth.npy", fs=500)

    result = AVAILABLE_METRICS["mse"]().compute(real.data, synth.data, lead_names=real.lead_names)
    print("MSE:", result.score, "RMSE:", result.extra["rmse"], "real vs real:", result.extra["real_vs_real"])
    ```

For paired data (for example reconstructed leads), add `--pairing paired` on the command line
or pass `pairing="paired"` to the constructor.

Parameters are in the [Metric Reference](../user-guide/metric-reference.md#mse).

## Learn more

- Wang & Bovik (2009). Mean squared error: Love it or leave it?
  *IEEE Signal Processing Magazine* 26(1), 98–117.
  [doi:10.1109/MSP.2008.930649](https://doi.org/10.1109/MSP.2008.930649)
- Related: [MAE](mae.md) (absolute instead of squared error), [PRD](prd.md) (relative to the
  signal energy), [PSNR](psnr.md) (MSE in decibels), [Euclidean distance](euclidean.md).
- How papers use it: [Paper Database](../literature/database.md#metrics/Fidelity), families *RMSE* and *MSE*.
