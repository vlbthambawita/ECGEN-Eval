# Fréchet Distance (FD)

**Key:** `fd` · **Family:** distribution · **Better:** lower ↓ · **Per-lead:** yes

FD asks: *do simple statistics of the signals (amplitude, spread, shape and frequency content)
follow the same joint distribution in the real and synthetic sets?* It uses the same Fréchet
formula as [FED](fed.md), but on 11 handcrafted features instead of deep embeddings, so it
needs no neural network or GPU.

## Try it

Each dot is one ECG lead described by two of its features (z-scored). FD fits a Gaussian to
each cloud and measures the distance between the two Gaussians.

<div class="mviz" data-viz="frechet" data-variant="fd">Interactive demo loading… (needs JavaScript)</div>

What to notice:

- The **mean term** grows when the synthetic features are systematically off, for example
  amplitudes that are too low.
- The **covariance term** grows when the synthetic set is too uniform (*too little variety*),
  too varied, or when features co-vary the wrong way (*wrong correlation*).
- With **few samples**, even identical distributions score above 0. Compare against the
  real-vs-real noise floor.

## How it works

For each lead separately:

1. Compute **11 features** per recording: mean, standard deviation, skewness, kurtosis, RMS,
   energy, maximum |x|, zero-crossing rate, lag-1 autocorrelation, spectral centroid and
   spectral bandwidth.
2. **Z-score** the features so that each has a comparable scale.
3. Fit a Gaussian (mean vector and covariance matrix) to the real features and another to the
   synthetic features.
4. Compute the Fréchet distance between them.

The overall score is the mean over leads.

## The math

\[
\mathrm{FD} = \lVert \mu_r - \mu_s \rVert_2^2 +
\operatorname{Tr}\!\left(\Sigma_r + \Sigma_s - 2\,(\Sigma_r\Sigma_s)^{1/2}\right)
\]

with \(\mu, \Sigma\) the mean and covariance of the 11-dimensional feature vectors, and
\(\varepsilon = 10^{-6}\) added to the covariance diagonals. For two 2-D Gaussians (as in
the demo) the trace of the matrix square root has a closed form,
\(\operatorname{Tr}\sqrt{AB} = \sqrt{\operatorname{Tr}(AB) + 2\sqrt{\det(AB)}}\).

## Reading the score

- **0** means identical feature means and covariances. There is no upper bound.
- FD only sees what the 11 features capture. Two sets with similar global statistics but
  different beat morphology can score well. Pair it with a morphology metric such as
  [SQI](sqi.md), or with [FED](fed.md).
- Like every Fréchet distance it is biased upward for small samples. Keep the number of
  recordings fixed across models (`n_subsample`, default 2000).
- Per-lead scores show which leads the generator struggles with.

## Use it with ECGEN-Eval

=== "CLI"

    ```bash
    ecgen-eval eval --real real.npy --synthetic synth.npy -m fd --output report.html
    ```

=== "Python"

    ```python
    from ecgen_eval import load_ecg_npy, AVAILABLE_METRICS

    real = load_ecg_npy("real.npy", fs=500)
    synth = load_ecg_npy("synth.npy", fs=500)

    result = AVAILABLE_METRICS["fd"]().compute(real.data, synth.data, lead_names=real.lead_names)
    print(result.score)            # mean over leads
    print(result.per_lead_scores)  # {"I": ..., "II": ..., ...}
    ```

Parameters (`n_subsample`, `eps`) are in the [Metric Reference](../user-guide/metric-reference.md#fd).

## Learn more

- Heusel et al., NeurIPS 2017 (FID); applied to ECG with handcrafted features in Thambawita
  et al., *Scientific Reports* 2021.
- [FED](fed.md) replaces the handcrafted features with foundation-model embeddings.
