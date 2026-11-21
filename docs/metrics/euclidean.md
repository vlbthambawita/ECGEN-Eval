# Euclidean Distance

**Key:** `euclidean` · **Family:** signal fidelity · **Better:** lower ↓ · **Per-lead:** yes

The Euclidean distance asks: *how far apart are a real and a synthetic ECG when each is seen
as one point with a coordinate per sample?* It is the straight-line (L2) distance in the time
domain. 12 papers in the [literature review](../literature/database.md#metrics/Fidelity) report it.

It carries the same information as RMSE: \(\mathrm{ED} = \sqrt{T}\cdot\mathrm{RMSE}\),
where \(T\) is the number of samples.

## Try it

<div class="mviz" data-viz="pointwise" data-highlight="euclidean">Interactive demo loading… (needs JavaScript)</div>

What to notice:

- The Euclidean distance always moves with RMSE; only the scale differs (by \(\sqrt{T}\)).
- **20 ms late**: a small shift gives a large distance. This is why [P140](../literature/database.md#papers/P140) calls it
  unsuitable for comparing morphology.

## How it works

1. Per lead, optionally normalise every recording (`normalize`).
2. Match real and synthetic signals according to `pairing` (default: nearest neighbour).
3. Compute the L2 distance of every pair and average over pairs, then over leads.

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
\mathrm{ED}(x_r, x_s) = \sqrt{\sum_{t=1}^{T} \big(x_r[t]-x_s[t]\big)^2}
\]

## Reading the score

- In signal units, and it **grows with the recording length**: a 10 s recording scores twice
  as high as a 2.5 s recording with the same error per sample. Compare only recordings of
  equal length and sampling rate, or use `extra["length_normalised"]` (identical to
  [`rmse`](mse.md)).
- `extra["real_vs_real"]` holds the same statistic between two disjoint halves of the real
  set. Read the score against it. [P012](../literature/database.md#papers/P012) reports 1.74 between two real sets against 1.75 to 2.01 for
  generators.
- Point-wise distances reward copying the training data and punish timing shifts
  ([P171](../literature/database.md#papers/P171)). Check [`nn_dist`](nn_dist.md) and [`dtw`](dtw.md) alongside.

[`nn_dist`](nn_dist.md) is also a nearest-neighbour Euclidean distance, but in a 7-feature
statistical space and used to detect memorisation. `euclidean` works on the waveform.

## Use it with ECGEN-Eval

=== "CLI"

    ```bash
    ecgen-eval eval --real real.npy --synthetic synth.npy -m euclidean --output report.html
    ```

=== "Python"

    ```python
    from ecgen_eval import load_ecg_npy, AVAILABLE_METRICS

    real = load_ecg_npy("real.npy", fs=500)
    synth = load_ecg_npy("synth.npy", fs=500)

    result = AVAILABLE_METRICS["euclidean"]().compute(real.data, synth.data, lead_names=real.lead_names)
    print("ED:", result.score, "per sample:", result.extra["length_normalised"])
    ```

Parameters are in the [Metric Reference](../user-guide/metric-reference.md#euclidean).

## Learn more

- Wang et al. (2013). Experimental comparison of representation methods and distance
  measures for time series data. *Data Mining and Knowledge Discovery* 26, 275–309.
  [doi:10.1007/s10618-012-0250-5](https://doi.org/10.1007/s10618-012-0250-5)
- Related: [MSE and RMSE](mse.md), [DTW](dtw.md), [Curve Fréchet distance](curve_frechet.md).
