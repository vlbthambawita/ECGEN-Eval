# Curve Fréchet Distance

**Key:** `curve_frechet` · **Family:** signal fidelity · **Better:** lower ↓ · **Per-lead:** yes

The discrete Fréchet distance asks: *if one walker follows the real waveform and another
follows the synthetic one, both only moving forward, how long must the leash between them
be?* Like DTW it may align the two curves in time first. Unlike DTW it reports only the
**single largest** remaining gap, not the sum of all gaps. 24 papers in the
[literature review](../literature/database.md#metrics/Fidelity) report it.

!!! warning "Not the Fréchet distance of `fd` and `fed`"
    Papers write "FD" for two unrelated quantities. This page is about the distance between
    two **curves**. [`fd`](fd.md) and [`fed`](fed.md) measure the distance between two
    **Gaussian distributions** fitted to features. Check which one a paper means before
    comparing numbers; several papers in the review do not say.

## Try it

Thin purple lines show the coupling: which real point is compared with which synthetic
point. The red line is the largest gap along that coupling, which is the score.

<div class="mviz" data-viz="curveFrechet">Interactive demo loading… (needs JavaScript)</div>

What to notice:

- **Shifted 40 ms**: the score is close to 0. With the default settings warping in time is
  free, so a pure shift costs nothing. The "largest gap without warping" read-out shows what
  a point-wise comparison would see.
- **Same shift, time costs**: with a time weight above 0 the leash also has to span the time
  difference, and the shift becomes visible.
- **R peak 30 % lower**: the score equals the height difference of the R peak. One point
  decides the whole score.
- **Inverted T wave**: the T wave now sets the score, although the RMSE is small.

## How it works

1. Decimate both signals to at most `max_len` points (default 500), because the computation
   grows with the product of the two lengths.
2. Match real and synthetic signals according to `pairing`. With the default `"nn"`, each of
   `n_pairs` real signals is matched to its nearest synthetic signal (Euclidean distance on
   the decimated signals).
3. Fill the coupling table \(c(i,j)\) from the formula below; the distance is its last entry.
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

For curves \(P = (p_1, \dots, p_n)\) and \(Q = (q_1, \dots, q_m)\) with point distance
\(d\):

\[
c(i,j) = \max\Big(\min\big(c(i-1,j),\; c(i-1,j-1),\; c(i,j-1)\big),\; d(p_i, q_j)\Big),
\qquad \mathrm{DFD}(P,Q) = c(n,m)
\]

The point distance depends on `time_weight` \(w\):

\[
d(p_i, q_j) = \sqrt{\big(x_r[i]-x_s[j]\big)^2 + \big(w\,(t_i - t_j)\big)^2}
\]

With the default \(w = 0\) only amplitudes are compared and the result is in signal units.
With \(w > 0\) (in signal units per second) time differences count as well.

## Reading the score

- 0 = identical curves (up to time warping when `time_weight=0`). The value is the largest
  amplitude gap that no monotone alignment can avoid, usually at the R peak.
- It is driven by **one point**, so a single artefact sets the score and everything else is
  ignored. [P012](../literature/database.md#papers/P012) found it barely separates generators (0.3318 against 0.3346) and warns
  that it can mislead.
- Values in papers range from 0.01 to 100, because amplitude units, signal length and the
  handling of the time axis differ and are rarely stated. Compare only with papers that
  state them, and report `time_weight`, `max_len` and the pairing with your number.
- `extra["real_vs_real"]` holds the same statistic between two disjoint halves of the real
  set. Read the score against it.

## Use it with ECGEN-Eval

=== "CLI"

    ```bash
    ecgen-eval eval --real real.npy --synthetic synth.npy -m curve_frechet --output report.html
    ```

=== "Python"

    ```python
    from ecgen_eval import load_ecg_npy, AVAILABLE_METRICS

    real = load_ecg_npy("real.npy", fs=500)
    synth = load_ecg_npy("synth.npy", fs=500)

    result = AVAILABLE_METRICS["curve_frechet"]().compute(real.data, synth.data, lead_names=real.lead_names)
    print("DFD:", result.score, "real vs real:", result.extra["real_vs_real"])
    ```

```python
# Make timing count: 1 mV per 100 ms of misalignment
metric = AVAILABLE_METRICS["curve_frechet"](time_weight=10.0, fs=real.fs)
```

Parameters are in the [Metric Reference](../user-guide/metric-reference.md#curve_frechet).

## Learn more

- Eiter & Mannila (1994). Computing discrete Fréchet distance. Technical Report CD-TR 94/64,
  TU Vienna.
- Delaney, Brophy & Ward (2019). Synthesis of realistic ECG using generative adversarial
  networks. [arXiv:1909.09150](https://arxiv.org/abs/1909.09150)
- Related: [DTW](dtw.md) (sums the gaps instead of taking the largest),
  [Fréchet Distance](fd.md) and [FED](fed.md) (distribution-level, different quantity).
