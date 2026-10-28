# Maximum Mean Discrepancy (MMD)

**Key:** `mmd` · **Family:** distribution · **Better:** lower ↓ · **Per-lead:** yes

MMD asks: *could the real and synthetic feature values have come from the same distribution?*
Unlike Fréchet distances it does not assume Gaussians, so it also detects differences in
**shape**, such as two modes where there should be one.

## Try it

The ticks at the bottom are individual recordings (one feature value each). Each curve is
the **kernel mean embedding** of one set: the average of a bump placed on every sample. MMD
measures how different the two curves are (shaded area).

<div class="mviz" data-viz="mmd">Interactive demo loading… (needs JavaScript)</div>

What to notice:

- **Two modes, same mean & variance**: the Fréchet number, which only looks at mean and
  variance, stays near 0, but MMD clearly rises. This is MMD's main advantage.
- The **kernel width** controls what MMD notices. Narrow kernels see fine detail (and noise);
  wide kernels only see coarse differences. ECGEN-Eval averages three widths (0.1, 1 and
  10 × the median distance) so the score is not tied to one choice.

## How it works

For each lead:

1. Describe every recording with the **7-feature descriptor**: mean, standard deviation,
   RMS, maximum |x|, energy, zero-crossing rate and lag-1 autocorrelation.
2. Compute kernel similarities between all pairs: real–real, synthetic–synthetic and
   real–synthetic. The kernel is the average of three RBF kernels whose widths are 0.1, 1 and
   10 × the **median squared distance** of that pair set (the median heuristic).
3. Combine them into the unbiased MMD² estimate below. Negative estimates (sampling noise)
   are clipped to 0.

## The math

With a kernel \(k\), real samples \(x_1..x_n\) and synthetic samples \(y_1..y_m\):

\[
\widehat{\mathrm{MMD}}^2 = \frac{1}{n(n-1)}\sum_{i\neq j} k(x_i,x_j)
+ \frac{1}{m(m-1)}\sum_{i\neq j} k(y_i,y_j)
- \frac{2}{nm}\sum_{i,j} k(x_i,y_j)
\]

\[
k(a,b) = \frac{1}{3}\sum_{\beta\in\{0.1,\,1,\,10\}} \exp\!\left(-\frac{\lVert a-b\rVert^2}{2\,\beta\,\sigma^2}\right),
\qquad \sigma^2 = \operatorname{median}\lVert a-b\rVert^2
\]

MMD is the distance between the two kernel mean embeddings
\(\mu_P(t) = \mathbb E_{x\sim P}[k(x,t)]\), which are the curves in the demo. With a
characteristic kernel such as the RBF, MMD = 0 **only if** the distributions are identical.

## Reading the score

- **0** means the sets are indistinguishable at the chosen kernel scales. Values are small
  (often below 0.1), so compare relative to a real-vs-real baseline.
- MMD values depend on the features and kernel settings. Compare models only under identical
  settings.
- On the 7 simple features, MMD can miss morphological differences that do not change those
  statistics. The literature also reports cases where MMD failed to separate real from
  synthetic data while a classifier succeeded (see the
  [literature review](../literature/index.md)).

## Use it with ECGEN-Eval

=== "CLI"

    ```bash
    ecgen-eval eval --real real.npy --synthetic synth.npy -m mmd --output report.html
    ```

=== "Python"

    ```python
    from ecgen_eval import load_ecg_npy, AVAILABLE_METRICS

    real = load_ecg_npy("real.npy", fs=500)
    synth = load_ecg_npy("synth.npy", fs=500)

    mmd = AVAILABLE_METRICS["mmd"](kernel_bandwidths=[0.1, 1.0, 10.0])
    result = mmd.compute(real.data, synth.data, lead_names=real.lead_names)
    print(result.score, result.extra["per_lead_mmd2"])
    ```

Parameters are in the [Metric Reference](../user-guide/metric-reference.md#mmd).

## Learn more

- Gretton et al., *A Kernel Two-Sample Test*, JMLR 13, 2012.
- Compare with [Fréchet Distance](fd.md), which only matches means and covariances, and with
  [Sliced Wasserstein](swd.md), another assumption-free distance.
