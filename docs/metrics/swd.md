# Sliced Wasserstein Distance (SWD)

**Key:** `swd` · **Family:** distribution · **Better:** lower ↓ · **Per-lead:** yes

SWD asks: *how much work would it take to move the synthetic distribution onto the real one?*
That transport cost (the Wasserstein distance) is hard to compute in many dimensions but easy
in one. SWD therefore projects the data onto many random lines and averages the 1-D costs.

## Try it

The purple line is one projection direction. The histograms show where the points land on
that line. The bottom chart shows the 1-D distance W₁ for every angle; SWD is its average.

<div class="mviz" data-viz="swd">Interactive demo loading… (needs JavaScript)</div>

What to notice:

- **Shift along x**: projections along x (0°) show the gap, while projections near 90° do
  not. One direction can miss a difference, so many directions are averaged.
- **Same marginals, wrong correlation**: the x and y histograms alone look identical, yet
  projections at 45° and 135° disagree. Slicing at many angles catches differences in how
  features co-vary.

## How it works

For each lead:

1. Describe every recording with the **7-feature descriptor** (mean, standard deviation,
   RMS, maximum |x|, energy, zero-crossing rate, lag-1 autocorrelation).
2. Draw `n_projections` (default 200) random unit directions with a fixed seed.
3. Project both sets onto each direction and compute the exact 1-D Wasserstein-1 distance by
   **sorting** the projected values and averaging the absolute differences of the matching
   quantiles.
4. Average over directions.

## The math

\[
\mathrm{SWD}(P, Q) = \frac{1}{K}\sum_{k=1}^{K} W_1\!\left(\theta_k^\top P,\ \theta_k^\top Q\right),
\qquad
W_1(a,b) = \frac{1}{n}\sum_{i=1}^{n} \left| a_{(i)} - b_{(i)} \right|
\]

where \(\theta_k\) are random unit vectors and \(a_{(i)}\) are the sorted projected values.
In 1-D the optimal transport plan simply matches the *i*-th smallest value with the *i*-th
smallest value, which is why sorting is enough.

## Reading the score

- **0** means every projection matches. The score is in feature units: comparable across
  models on the same data, not across data sets.
- SWD makes no Gaussian assumption and is cheap: \(O(K\,n\log n)\).
- With few projections in high dimensions, some differences can be missed; 200 directions is
  plenty for 7 features.

## Use it with ECGEN-Eval

=== "CLI"

    ```bash
    ecgen-eval eval --real real.npy --synthetic synth.npy -m swd --output report.html
    ```

=== "Python"

    ```python
    from ecgen_eval import load_ecg_npy, AVAILABLE_METRICS

    real = load_ecg_npy("real.npy", fs=500)
    synth = load_ecg_npy("synth.npy", fs=500)

    swd = AVAILABLE_METRICS["swd"](n_projections=200, seed=42)
    result = swd.compute(real.data, synth.data, lead_names=real.lead_names)
    print(result.score, result.per_lead_scores)
    ```

Parameters are in the [Metric Reference](../user-guide/metric-reference.md#swd).

## Learn more

- Rabin et al., *Wasserstein Barycenter and its Application to Texture Mixing*, 2011.
- Kolouri et al., *Generalized Sliced Wasserstein Distances*, NeurIPS 2019.
