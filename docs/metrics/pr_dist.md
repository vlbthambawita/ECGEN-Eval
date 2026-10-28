# Precision & Recall (`pr_dist`)

**Key:** `pr_dist` · **Family:** distribution · **Better:** higher ↑ · **Per-lead:** yes

A single distance cannot tell *bad samples* from *missing variety*. Precision and recall
separate the two:

- **Precision**: *are the synthetic ECGs realistic?* (Do they fall where real ECGs live?)
- **Recall**: *is the real variety covered?* (Does every kind of real ECG have synthetic
  neighbours?)

The score is their harmonic mean (F-score).

## Try it

The real data has a large mode (think normal beats) and a small one (think ectopic beats).
Each point gets a ball reaching to its *k*-th nearest neighbour; the union of balls estimates
the data manifold. Hollow points fall outside the other set's manifold.

<div class="mviz" data-viz="prdist">Interactive demo loading… (needs JavaScript)</div>

What to notice:

- **Mode dropped**: precision stays high (every synthetic sample is realistic), but recall
  falls because the small real mode has no synthetic neighbours. This is classic mode
  collapse, and a single distance score would not explain it.
- **Too narrow**: realistic but repetitive samples give high precision and low recall.
- **Too noisy**: synthetic samples scatter outside the real manifold, so precision drops.
- Larger **k** makes the balls bigger, so both numbers become more forgiving.

## How it works

For each lead:

1. Describe every recording with the **7-feature descriptor** and divide each feature by
   its standard deviation in the real set.
2. For each real point, compute the distance to its *k*-th nearest real neighbour (its
   radius). Do the same within the synthetic set.
3. **Precision** = fraction of synthetic points whose nearest real point is within that real
   point's radius.
4. **Recall** = fraction of real points whose nearest synthetic point is within that
   synthetic point's radius.
5. Score = \(F = 2PR/(P+R)\). The overall score is the mean over leads.

!!! note "Nearest-neighbour rule"
    ECGEN-Eval checks only the ball of the **nearest** point, which is slightly stricter than
    Kynkäänniemi et al. (2019), who check the balls of all points. The demo uses the same
    rule as the code.

## The math

\[
\mathrm{precision} = \frac{1}{m}\sum_{j=1}^{m}
\mathbb 1\!\left[\lVert y_j - x_{\mathrm{nn}(j)}\rVert \le r_k(x_{\mathrm{nn}(j)})\right],
\qquad
\mathrm{recall} = \frac{1}{n}\sum_{i=1}^{n}
\mathbb 1\!\left[\lVert x_i - y_{\mathrm{nn}(i)}\rVert \le r_k(y_{\mathrm{nn}(i)})\right]
\]

where \(r_k(\cdot)\) is the distance to the *k*-th nearest neighbour within the point's own set.

## Reading the score

- Range **[0, 1]**, higher is better. Always look at precision and recall separately: they
  are in `result.extra["precision"]` and `result.extra["recall"]`.
- Low precision means unrealistic samples; low recall means mode collapse or missing classes.
- Outliers in the real data inflate radii and make precision easier to reach. Density and
  coverage (Naeem et al., 2020) are more robust variants.

## Use it with ECGEN-Eval

=== "CLI"

    ```bash
    ecgen-eval eval --real real.npy --synthetic synth.npy -m pr_dist --output report.html
    ```

=== "Python"

    ```python
    from ecgen_eval import load_ecg_npy, AVAILABLE_METRICS

    real = load_ecg_npy("real.npy", fs=500)
    synth = load_ecg_npy("synth.npy", fs=500)

    result = AVAILABLE_METRICS["pr_dist"](k=3).compute(real.data, synth.data, lead_names=real.lead_names)
    print("F:", result.score)
    print("precision:", result.extra["precision"])
    print("recall:", result.extra["recall"])
    ```

Parameters are in the [Metric Reference](../user-guide/metric-reference.md#pr_dist).

## Learn more

- Kynkäänniemi et al., *Improved Precision and Recall Metric for Assessing Generative
  Models*, NeurIPS 2019.
- Naeem et al., *Reliable Fidelity and Diversity Metrics for Generative Models*, ICML 2020.
