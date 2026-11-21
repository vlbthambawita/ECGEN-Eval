# Pearson Correlation

**Key:** `pearson` · **Family:** signal fidelity · **Better:** higher ↑ · **Per-lead:** yes

Pearson correlation asks: *do the real and the synthetic waveform go up and down together?*
It compares **shape** only. Amplitude scale and baseline offset are removed before the
comparison. It is the most used fidelity metric that ECGEN-Eval did not have: 41 papers in the
[literature review](../literature/database.md#metrics/Fidelity).

## Try it

<div class="mviz" data-viz="pointwise" data-highlight="pearson">Interactive demo loading… (needs JavaScript)</div>

What to notice:

- Move **Amplitude** or **Baseline offset**: Pearson stays at 1.000 while MSE and RMSE grow.
  Pearson cannot see a gain or offset error.
- **Baseline drift** separates Pearson from cosine similarity: the offset changes cosine but
  not Pearson.
- **20 ms late**: Pearson drops sharply, as every point-wise metric does.
- **Inverted T wave**: Pearson falls to about 0.64. That is a smaller drop than for the
  20 ms shift (about 0.37): a timing offset a cardiologist would ignore is punished harder
  than an inverted T wave.

## How it works

1. Per lead, remove each recording's mean and scale it to unit length.
2. Match real and synthetic signals according to `pairing`. With the default `"nn"`, each real
   signal is matched to the synthetic signal it **correlates best** with.
3. The correlation of a pair is the dot product of the two normalised signals.
4. Average over pairs, then over leads.

Flat signals (zero variance) have no defined correlation. Those pairs are skipped and counted
in `extra["n_skipped"]`.

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
r = \frac{\sum_t (x_r[t]-\bar x_r)(x_s[t]-\bar x_s)}
{\sqrt{\sum_t (x_r[t]-\bar x_r)^2}\;\sqrt{\sum_t (x_s[t]-\bar x_s)^2}}
\]

With `max_lag_ms > 0`, ECGEN-Eval also reports the largest normalised cross-correlation within
±`max_lag_ms` (`extra["xcorr_max"]`) and the lag where it occurs (`extra["best_lag_ms"]`,
positive when the synthetic signal is late). The score itself stays the zero-lag value.

## Reading the score

- Range \([-1, 1]\): 1 = same shape, 0 = unrelated, −1 = inverted.
- `extra["real_vs_real"]` holds the same statistic between two disjoint halves of the real
  set. Read the score against it. [P012](../literature/database.md#papers/P012) reports 0.66 between two real test sets, 0.65 for the best
  generator and 0.60 for the weakest: differences between models are small, and real data
  does not reach 1.
- Paired values above 0.9 are typical for reconstruction and translation tasks, and for
  aligned single beats Pearson is near 1 for almost any model ([P171](../literature/database.md#papers/P171)), so it separates
  models poorly there.
- Because gain and offset are invisible to it, always report an amplitude-sensitive metric
  ([`rmse`](mse.md), [`js_div`](js_div.md)) next to it.

[`sqi`](sqi.md) also uses Pearson correlation, but against the **mean real template** of each
lead. `pearson` compares individual signals.

## Use it with ECGEN-Eval

=== "CLI"

    ```bash
    ecgen-eval eval --real real.npy --synthetic synth.npy -m pearson --output report.html
    ```

=== "Python"

    ```python
    from ecgen_eval import load_ecg_npy, AVAILABLE_METRICS

    real = load_ecg_npy("real.npy", fs=500)
    synth = load_ecg_npy("synth.npy", fs=500)

    result = AVAILABLE_METRICS["pearson"]().compute(real.data, synth.data, lead_names=real.lead_names)
    print("r:", result.score, "real vs real:", result.extra["real_vs_real"])
    ```

```python
# Tolerate small timing offsets: best cross-correlation within ±40 ms
metric = AVAILABLE_METRICS["pearson"](pairing="paired", max_lag_ms=40, fs=real.fs)
result = metric.compute(real.data, synth.data)
print(result.extra["xcorr_max"], result.extra["best_lag_ms"])
```

Parameters are in the [Metric Reference](../user-guide/metric-reference.md#pearson).

## Learn more

- Pearson (1895). Note on regression and inheritance in the case of two parents.
  *Proc. R. Soc. London* 58, 240–242.
  [doi:10.1098/rspl.1895.0041](https://doi.org/10.1098/rspl.1895.0041)
- [P012](../literature/database.md#papers/P012): Wang et al. (2025), *Advancing electrocardiogram synthesis: Analyzing key
  metrics for enhanced evaluation*, recommends Pearson over cross-correlation and cosine
  similarity.
- Related: [Cosine similarity](cosine.md), [SQI](sqi.md), [SSIM](ssim.md).
