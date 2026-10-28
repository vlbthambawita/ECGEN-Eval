# Metrics Overview

ECGEN-Eval ships 16 metrics, registered in
[`AVAILABLE_METRICS`](../api/metrics.md). Each one compares a **set** of real recordings with
a **set** of synthetic recordings — no pairing between individual samples is required.

```python
from ecgen_eval import AVAILABLE_METRICS

metric = AVAILABLE_METRICS["fd"]()                       # default parameters
metric = AVAILABLE_METRICS["dtw"](n_pairs=500, window=0.05)  # custom parameters
result = metric.compute(real.data, synth.data, lead_names=real.lead_names)
```

!!! tip "Learn how each metric works"
    [Metrics Explained](../metrics/index.md) has one page per metric with an interactive
    visualization, the maths, how to read the score, and usage examples.

## All metrics

[![The 16 metrics grouped into six families; arrows show whether lower or higher is better](../assets/diagrams/metric-families-light.svg#only-light){ .ecgen-diagram }](../assets/diagrams/metric-families-light.svg "Open full size")
[![The 16 metrics grouped into six families; arrows show whether lower or higher is better](../assets/diagrams/metric-families-dark.svg#only-dark){ .ecgen-diagram }](../assets/diagrams/metric-families-dark.svg "Open full size")

| Key | Name | Better | Family | Per-lead | Extra deps |
|---|---|:-:|---|:-:|---|
| [`mmd`](../metrics/mmd.md) | [Maximum Mean Discrepancy](../metrics/mmd.md) | ↓ | Distribution | ✓ | — |
| [`fd`](../metrics/fd.md) | [Fréchet Distance (handcrafted features)](../metrics/fd.md) | ↓ | Distribution | ✓ | — |
| [`fed`](../metrics/fed.md) | [Fréchet ECG Distance (foundation model)](../metrics/fed.md) | ↓ | Distribution | — | `[fed]` |
| [`swd`](../metrics/swd.md) | [Sliced Wasserstein Distance](../metrics/swd.md) | ↓ | Distribution | ✓ | — |
| [`pr_dist`](../metrics/pr_dist.md) | [Precision & Recall (F-score)](../metrics/pr_dist.md) | ↑ | Distribution | ✓ | — |
| [`dtw`](../metrics/dtw.md) | [Dynamic Time Warping](../metrics/dtw.md) | ↓ | Signal fidelity | ✓ | `dtaidistance` (bundled) |
| [`prd`](../metrics/prd.md) | [Percent RMS Difference](../metrics/prd.md) | ↓ | Signal fidelity | ✓ | — |
| [`mae`](../metrics/mae.md) | [Mean Absolute Error (NN)](../metrics/mae.md) | ↓ | Signal fidelity | ✓ | — |
| [`psnr`](../metrics/psnr.md) | [Peak Signal-to-Noise Ratio](../metrics/psnr.md) | ↑ | Signal fidelity | ✓ | — |
| [`ssim`](../metrics/ssim.md) | [Structural Similarity (1-D)](../metrics/ssim.md) | ↑ | Signal fidelity | ✓ | — |
| [`sqi`](../metrics/sqi.md) | [Signal Quality Index (template correlation)](../metrics/sqi.md) | ↑ | Morphology | ✓ | — |
| [`psd`](../metrics/psd.md) | [PSD Jensen–Shannon divergence](../metrics/psd.md) | ↓ | Spectral | ✓ | `scipy` (optional) |
| [`spectral_entropy`](../metrics/spectral_entropy.md) | [Spectral Entropy divergence](../metrics/spectral_entropy.md) | ↓ | Spectral | ✓ | `scipy` (optional) |
| [`hrv`](../metrics/hrv.md) | [HRV statistics divergence](../metrics/hrv.md) | ↓ | Physiological | ✓ | `scipy` (optional) |
| [`heart_rate`](../metrics/heart_rate.md) | [Heart-rate distribution divergence](../metrics/heart_rate.md) | ↓ | Physiological | ✓ | `scipy` (optional) |
| [`nn_dist`](../metrics/nn_dist.md) | [Nearest-Neighbour Distance (memorisation)](../metrics/nn_dist.md) | ↓ | Privacy | ✓ | — |

↓ lower is better · ↑ higher is better. The direction is also available programmatically as
`metric.higher_is_better` and `result.higher_is_better`.

## Which metric answers which question?

Distribution
:   *Does the synthetic set cover the same population as the real set?*
    [`mmd`](../metrics/mmd.md), [`fd`](../metrics/fd.md), [`swd`](../metrics/swd.md) and [`fed`](../metrics/fed.md) compare whole distributions; [`pr_dist`](../metrics/pr_dist.md) splits the answer into
    **precision** (are synthetic samples realistic?) and **recall** (is the real diversity covered?).

Signal fidelity
:   *Does each real ECG have a close synthetic look-alike?* [`prd`](../metrics/prd.md), [`mae`](../metrics/mae.md), [`psnr`](../metrics/psnr.md), [`ssim`](../metrics/ssim.md)
    match each real recording to its nearest synthetic neighbour and measure the waveform
    error. [`dtw`](../metrics/dtw.md) tolerates small temporal shifts.

Morphology
:   *Do synthetic beats have the right shape?* [`sqi`](../metrics/sqi.md) correlates synthetic signals with a
    template built from the real data.

Spectral
:   *Is the frequency content right?* [`psd`](../metrics/psd.md) compares mean power spectra; [`spectral_entropy`](../metrics/spectral_entropy.md)
    compares how spread-out each recording's spectrum is.

Physiological
:   *Is the cardiac rhythm plausible?* [`heart_rate`](../metrics/heart_rate.md) and [`hrv`](../metrics/hrv.md) detect R-peaks and compare the
    resulting heart-rate and HRV distributions. For a richer, clinically interpretable
    comparison see [Clinical Features](features.md).

Privacy
:   *Is the model copying training data?* [`nn_dist`](../metrics/nn_dist.md) reports nearest-neighbour distances, plus
    an **authenticity** score in `extra`. Very low nearest-neighbour distances or low
    authenticity can indicate memorisation.

!!! tip "A practical default set"
    For a quick but balanced picture use
    `-m fd -m mmd -m pr_dist -m psd -m hrv -m nn_dist`, and add [`fed`](../metrics/fed.md) when a GPU is available.

## Reading `MetricResult`

```python
result = AVAILABLE_METRICS["pr_dist"]().compute(real.data, synth.data, real.lead_names)

result.metric_name        # "pr_dist"
result.score              # overall F-score (mean over leads)
result.higher_is_better   # True
result.per_lead_scores    # {"I": 0.81, "II": 0.77, ...}
result.extra["precision"] # {"I": 0.90, ...}
result.extra["recall"]    # {"I": 0.74, ...}
result.summary_dict()     # JSON-friendly dict, rounded to 6 decimals
```

For per-lead metrics the overall `score` is the **mean of the per-lead scores**.

## Practical notes

Subsampling and reproducibility
:   Most metrics cap the number of recordings with `n_subsample` (500–2000 by default) and use
    a fixed `seed=42`, so repeated runs on the same data give the same score. Increase
    `n_subsample` for more stable estimates on large datasets.

Cost
:   Nearest-neighbour metrics (`prd`, `mae`, `psnr`, `ssim`) compare every real recording with
    every synthetic one, so time grows with `N_real × N_synth × T`. Reduce `n_subsample` to
    speed them up. `dtw` only evaluates `n_pairs` random pairs on
    downsampled signals. `fed` runs a neural network and is fastest on a GPU.

Sampling rate
:   `psd`, `spectral_entropy`, `hrv` and `heart_rate` take an `fs` argument (default 500 Hz).
    In Python, pass your sampling rate when constructing them:
    `AVAILABLE_METRICS["hrv"](fs=250)`. The `ecgen-eval eval` command does this automatically,
    using the sampling rate of the real dataset (`--fs`, or the rate in the WFDB headers).

Comparing scores across runs
:   Absolute values depend on the signal units, length and the subsampling settings. Compare
    models under identical settings and against a **real-vs-real baseline** (e.g. two disjoint
    halves of the real dataset) to know what a "good" score looks like.

See the [Metric Reference](metric-reference.md) for the definition, parameters and `extra`
contents of every metric.
