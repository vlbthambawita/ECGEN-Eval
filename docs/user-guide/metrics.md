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

## All metrics

| Key | Name | Better | Family | Per-lead | Extra deps |
|---|---|:-:|---|:-:|---|
| `mmd` | Maximum Mean Discrepancy | ↓ | Distribution | ✓ | — |
| `fd` | Fréchet Distance (handcrafted features) | ↓ | Distribution | ✓ | — |
| `fed` | Fréchet ECG Distance (foundation model) | ↓ | Distribution | — | `[fed]` |
| `swd` | Sliced Wasserstein Distance | ↓ | Distribution | ✓ | — |
| `pr_dist` | Precision & Recall (F-score) | ↑ | Distribution | ✓ | — |
| `dtw` | Dynamic Time Warping | ↓ | Signal fidelity | ✓ | `dtaidistance` (bundled) |
| `prd` | Percent RMS Difference | ↓ | Signal fidelity | ✓ | — |
| `mae` | Mean Absolute Error (NN) | ↓ | Signal fidelity | ✓ | — |
| `psnr` | Peak Signal-to-Noise Ratio | ↑ | Signal fidelity | ✓ | — |
| `ssim` | Structural Similarity (1-D) | ↑ | Signal fidelity | ✓ | — |
| `sqi` | Signal Quality Index (template correlation) | ↑ | Morphology | ✓ | — |
| `psd` | PSD Jensen–Shannon divergence | ↓ | Spectral | ✓ | `scipy` (optional) |
| `spectral_entropy` | Spectral Entropy divergence | ↓ | Spectral | ✓ | `scipy` (optional) |
| `hrv` | HRV statistics divergence | ↓ | Physiological | ✓ | `scipy` (optional) |
| `heart_rate` | Heart-rate distribution divergence | ↓ | Physiological | ✓ | `scipy` (optional) |
| `nn_dist` | Nearest-Neighbour Distance (memorisation) | ↓ | Privacy | ✓ | — |

↓ lower is better · ↑ higher is better. The direction is also available programmatically as
`metric.higher_is_better` and `result.higher_is_better`.

## Which metric answers which question?

Distribution
:   *Does the synthetic set cover the same population as the real set?*
    `mmd`, `fd`, `swd` and `fed` compare whole distributions; `pr_dist` splits the answer into
    **precision** (are synthetic samples realistic?) and **recall** (is the real diversity covered?).

Signal fidelity
:   *Does each real ECG have a close synthetic look-alike?* `prd`, `mae`, `psnr`, `ssim`
    match each real recording to its nearest synthetic neighbour and measure the waveform
    error. `dtw` tolerates small temporal shifts.

Morphology
:   *Do synthetic beats have the right shape?* `sqi` correlates synthetic signals with a
    template built from the real data.

Spectral
:   *Is the frequency content right?* `psd` compares mean power spectra; `spectral_entropy`
    compares how spread-out each recording's spectrum is.

Physiological
:   *Is the cardiac rhythm plausible?* `heart_rate` and `hrv` detect R-peaks and compare the
    resulting heart-rate and HRV distributions. For a richer, clinically interpretable
    comparison see [Clinical Features](features.md).

Privacy
:   *Is the model copying training data?* `nn_dist` reports nearest-neighbour distances, plus
    an **authenticity** score in `extra`. Very low nearest-neighbour distances or low
    authenticity can indicate memorisation.

!!! tip "A practical default set"
    For a quick but balanced picture use
    `-m fd -m mmd -m pr_dist -m psd -m hrv -m nn_dist`, and add `fed` when a GPU is available.

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
:   Nearest-neighbour metrics (`prd`, `mae`, `psnr`, `ssim`) build pairwise distance matrices
    over raw signals, so memory and time grow with `N_real × N_synth × T`. Reduce
    `n_subsample` if you run out of memory. `dtw` only evaluates `n_pairs` random pairs on
    downsampled signals. `fed` runs a neural network and is fastest on a GPU.

Sampling rate
:   `psd`, `spectral_entropy`, `hrv` and `heart_rate` take an `fs` argument (default 500 Hz).
    In Python, pass your sampling rate when constructing them:
    `AVAILABLE_METRICS["hrv"](fs=250)`.

    !!! warning
        The `ecgen-eval eval` command constructs these metrics with their defaults, so
        `--fs` only sets dataset metadata and does **not** change the metric `fs`. For data not
        sampled at 500 Hz, either resample to 500 Hz or run these metrics from Python.

Comparing scores across runs
:   Absolute values depend on the signal units, length and the subsampling settings. Compare
    models under identical settings and against a **real-vs-real baseline** (e.g. two disjoint
    halves of the real dataset) to know what a "good" score looks like.

See the [Metric Reference](metric-reference.md) for the definition, parameters and `extra`
contents of every metric.
