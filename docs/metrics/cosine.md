# Cosine Similarity

**Key:** `cosine` · **Family:** signal fidelity · **Better:** higher ↑ · **Per-lead:** yes

Cosine similarity treats each signal as a vector with one coordinate per sample and asks:
*do the real and the synthetic vector point in the same direction?* It is Pearson correlation
**without** removing the mean. 12 papers in the
[literature review](../literature/database.md#metrics/Fidelity) report it.

!!! warning "Implemented for reproducibility, not recommended for ranking models"
    [P012](../literature/database.md#papers/P012) found that cosine similarity ranked a GAN (0.849) above a second real test
    set (0.841) and concluded that it does not reflect quality. Use it to reproduce numbers
    from papers; prefer [`pearson`](pearson.md) for shape.

## Try it

<div class="mviz" data-viz="pointwise" data-highlight="cosine">Interactive demo loading… (needs JavaScript)</div>

What to notice:

- **Amplitude**: no effect. Scaling a vector does not change its direction.
- **Baseline drift**: cosine changes while Pearson stays at 1. In the demo the offset is added
  to the synthetic beat only, so cosine falls. An offset shared by both signals does the
  opposite: it makes any two signals look more similar.
- **20 ms late** and **Noisy**: cosine and Pearson fall together.

## How it works

1. Per lead, scale each recording to unit length (no mean removal).
2. Match real and synthetic signals according to `pairing`. With the default `"nn"`, each real
   signal is matched to its most similar synthetic signal.
3. The similarity of a pair is the dot product of the two scaled signals.
4. Average over pairs, then over leads. All-zero signals are skipped and counted in
   `extra["n_skipped"]`.

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
\cos(x_r, x_s) = \frac{\sum_t x_r[t]\,x_s[t]}{\lVert x_r\rVert\;\lVert x_s\rVert}
\]

For zero-mean signals this equals the Pearson correlation.

## Reading the score

- Range \([-1, 1]\); 1 = same direction.
- Values cluster near 1 for any plausible ECG, especially for average beats: [P011](../literature/database.md#papers/P011)
  reports ≥ 0.98 for every method and class. Small differences are not meaningful.
- A baseline offset inflates the score. Remove the baseline, or use Pearson.
- With `pairing="mean"`, all variation inside a class is averaged away before the comparison.
- `extra["real_vs_real"]` holds the same statistic between two disjoint halves of the real
  set. Read the score against it.

## Use it with ECGEN-Eval

=== "CLI"

    ```bash
    ecgen-eval eval --real real.npy --synthetic synth.npy -m cosine --output report.html
    ```

=== "Python"

    ```python
    from ecgen_eval import load_ecg_npy, AVAILABLE_METRICS

    real = load_ecg_npy("real.npy", fs=500)
    synth = load_ecg_npy("synth.npy", fs=500)

    result = AVAILABLE_METRICS["cosine"]().compute(real.data, synth.data, lead_names=real.lead_names)
    print("cosine:", result.score, "real vs real:", result.extra["real_vs_real"])
    ```

Parameters are in the [Metric Reference](../user-guide/metric-reference.md#cosine).

## Learn more

- Singhal (2001). Modern information retrieval: A brief overview. *IEEE Data Engineering
  Bulletin* 24(4), 35–43.
- Related: [Pearson correlation](pearson.md), [SSIM](ssim.md).
- How papers use it: [Paper Database](../literature/database.md#metrics/Fidelity), family *Cosine similarity*.
