# ECGEN-Eval

Evaluation metrics and interactive HTML reports for synthetic ECG quality assessment.
Part of the ECGEN research suite (ECGEN-FM, ECGEN-VAE, Pulse2Pulse).

📖 **Documentation:** <https://vajira.info/ECGEN-Eval/>

## Installation

```bash
pip install -e .           # core
pip install -e ".[dev]"    # + pytest, black, ruff
```

Optional dependencies:
```bash
pip install wfdb           # for loading PTB-XL / WFDB records
pip install scipy          # for Welch PSD, resampling, and R-peak detection (recommended)
pip install dtaidistance   # fast Cython DTW (falls back to pure-Python)

# Clinical feature extraction (Task 1.2)
pip install -e ".[features]"   # installs neurokit2 + scipy
# or individually:
pip install neurokit2 scipy
```

## Quick start

```python
import numpy as np
from ecgen_eval import load_ecg_npy, AVAILABLE_METRICS

# Load model outputs (shape: N × L × T)
real  = load_ecg_npy("real_ecgs.npy",  label="PTB-XL")
synth = load_ecg_npy("synth_ecgs.npy", label="ECGEN-FM")

# Compute a metric
mmd = AVAILABLE_METRICS["mmd"]()
result = mmd.compute(real.data, synth.data, lead_names=real.lead_names)
print(f"MMD = {result.score:.6f}")
print(result.per_lead_scores)
```

## Data loaders

| Function | Input | Use case |
|---|---|---|
| `load_ecg_npy(path)` | `.npy` / `.npz` (N, L, T) | ECGEN-FM, ECGEN-VAE, Pulse2Pulse outputs |
| `load_ecg_wfdb(dir)` | WFDB `.hea`/`.dat` records | PTB-XL and PhysioNet datasets |
| `load_ecg_folder(path)` | auto-detected | Any of the above + CSV |

`load_ecg_folder` auto-detects the format based on file extensions.

## Metrics

All metrics are available via `AVAILABLE_METRICS["key"]()` and return a `MetricResult`
with `.score`, `.per_lead_scores`, and `.extra`.

### Original metrics

| Key | Name | Lower / Higher | Paper |
|---|---|---|---|
| `mmd` | Maximum Mean Discrepancy | Lower ↓ | [Gretton et al., JMLR 2012](https://jmlr.org/papers/v13/gretton12a.html) |
| `dtw` | Dynamic Time Warping | Lower ↓ | [Berndt & Clifford, KDD 1994](https://dl.acm.org/doi/10.5555/3000850.3000887) |
| `prd` | Percent Root-mean-square Difference | Lower ↓ | [Zigel et al., IEEE TBME 2000](https://doi.org/10.1109/10.871206) |
| `psd` | PSD Divergence (Jensen-Shannon) | Lower ↓ | [Welch, IEEE Trans Audio 1967](https://doi.org/10.1109/TAU.1967.1161901) · Applied: [Golany & Radinsky, AAAI 2019](https://doi.org/10.1609/aaai.v33i01.3301557) |
| `fd` | Fréchet Distance | Lower ↓ | [Heusel et al., NeurIPS 2017](https://proceedings.neurips.cc/paper/2017/hash/8a1d694707eb0fefe65871369074926d-Abstract.html) · Applied: [Thambawita et al., Sci Rep 2021](https://doi.org/10.1038/s41598-021-01295-2) |

### New metrics (literature review 2018 – 2025)

| Key | Name | Lower / Higher | Paper |
|---|---|---|---|
| `psnr` | Peak Signal-to-Noise Ratio | Higher ↑ | [Huynh-Thu & Ghanbari, Electron Lett 2008](https://doi.org/10.1049/el:20080522) |
| `ssim` | Structural Similarity Index (1-D) | Higher ↑ | [Wang et al., IEEE TIP 2004](https://doi.org/10.1109/TIP.2003.819861) · ECG: [Hayn et al., Physiol Meas 2018](https://doi.org/10.1088/1361-6579/aa9f5b) |
| `swd` | Sliced Wasserstein Distance | Lower ↓ | [Rabin et al., LNCS 2011](https://doi.org/10.1007/978-3-642-24785-9_37) · [Kolouri et al., NeurIPS 2019](https://proceedings.neurips.cc/paper/2019/hash/f0935e4cd5920aa6c7c996a5ee53a70f-Abstract.html) |
| `mae` | Mean Absolute Error (nearest-neighbour) | Lower ↓ | [Zigel et al., IEEE TBME 2000](https://doi.org/10.1109/10.871206) |
| `hrv` | Heart Rate Variability (SDNN/rMSSD/pNN50) | Lower ↓ | [Task Force ESC/NASPE, Circulation 1996](https://doi.org/10.1161/01.CIR.93.5.1043) |
| `pr_dist` | Distribution Precision & Recall | Higher ↑ | [Kynkäänniemi et al., NeurIPS 2019](https://proceedings.neurips.cc/paper/2019/hash/0234c510bc6d908b28c70ff313743079-Abstract.html) |
| `sqi` | Signal Quality Index (QRS template) | Higher ↑ | [Clifford et al., CinC 2017](https://doi.org/10.22489/CinC.2017.065-469) |
| `nn_dist` | Nearest-Neighbour Distance (memorisation) | Lower ↓ | [Meehan et al., AISTATS 2020](https://proceedings.mlr.press/v119/meehan20a.html) |
| `heart_rate` | Heart Rate Distribution (JS divergence) | Lower ↓ | [Pan & Tompkins, IEEE TBME 1985](https://doi.org/10.1109/TBME.1985.325532) · Applied: [Golany & Radinsky, AAAI 2019](https://doi.org/10.1609/aaai.v33i01.3301557) |
| `spectral_entropy` | Spectral Entropy Divergence | Lower ↓ | [Inouye et al., EEG Clin Neurophysiol 1991](https://doi.org/10.1016/0013-4694(91)90138-T) |

## Feature Extraction

Extract 10 clinical ECG features per recording and compare their distributions between real and synthetic datasets.

```python
from ecgen_eval import load_ecg_npy
from ecgen_eval.features import extract_features

real  = load_ecg_npy("real_ecgs.npy",  label="PTB-XL")
synth = load_ecg_npy("synth_ecgs.npy", label="ECGEN-FM")

# Returns (beat_df, summary_df)
_, real_feat  = extract_features(real)
_, synth_feat = extract_features(synth)

print(real_feat[["rr_mean_ms", "hr_bpm", "qrs_duration_ms",
                  "qt_interval_ms", "hrv_sdnn_ms"]].describe())
```

Extracted features (one value per recording):

| Feature | Column | Description |
|---------|--------|-------------|
| RR interval | `rr_mean_ms`, `rr_std_ms` | Mean and std of peak-to-peak intervals |
| Heart rate | `hr_bpm` | 60 000 / mean(RR) |
| PR interval | `pr_interval_ms` | P-onset to QRS-onset |
| QRS duration | `qrs_duration_ms` | Width of QRS complex |
| QT interval | `qt_interval_ms` | QRS-onset to T-end |
| QTc (Bazett) | `qtc_bazett_ms` | QT / √RR(s) |
| ST deviation | `st_deviation_mv` | Mean ST voltage vs isoelectric line |
| T-wave amplitude | `t_amplitude_mv` | Signed T-peak amplitude |
| P-wave duration | `p_wave_duration_ms` | P-onset to P-offset |
| HRV | `hrv_sdnn_ms`, `hrv_rmssd_ms`, `hrv_pnn50` | SDNN, RMSSD, pNN50 |

### 2D and 3D distribution plots

```python
from ecgen_eval.visualization.feature_plots import (
    plot_feature_2d,
    plot_feature_pair_grid,
    plot_feature_3d,
    plot_feature_triple_grid,
)

# Single 2D scatter + KDE contour
fig = plot_feature_2d(real_feat, synth_feat, "rr_mean_ms", "hr_bpm")
fig.show()

# Grid of default feature pairs
fig = plot_feature_pair_grid(real_feat, synth_feat)
fig.show()

# Interactive 3D scatter
fig = plot_feature_3d(real_feat, synth_feat, "rr_mean_ms", "hr_bpm", "qrs_duration_ms")
fig.show()
```

## CLI

```bash
# Run all metrics and generate interactive HTML report
ecgen-eval eval \
  --real   /path/to/real_ecgs.npy \
  --synthetic /path/to/model1_ecgs.npy \
  --synthetic /path/to/model2_ecgs.npy \
  --output report.html

# Include clinical feature distributions in the report (requires neurokit2)
ecgen-eval eval \
  --real /path/to/real_ecgs.npy \
  --synthetic /path/to/synth_ecgs.npy \
  --feature-plots \
  --output report.html

# Extract features only — save summary CSV
ecgen-eval features \
  --real /path/to/real_ecgs.npy \
  --synthetic /path/to/synth_ecgs.npy \
  --output features.csv

# List available metrics
ecgen-eval list-metrics

# ECG waveform comparison only (no metrics)
ecgen-eval visualize \
  --real /path/to/real.npy \
  --synthetic /path/to/synth.npy \
  --compare-mode overlay
```

Key options for `eval`:
- `-m mmd -m prd -m psd` — run a subset of metrics (repeat `-m` per metric; default: all, including `fed`)
- `--feature-plots` — add clinical feature extraction + 2D/3D distribution plots
- `--fs 500` — sampling frequency
- `--n-samples 5` — ECG samples shown in gallery
- `--offline` — embed Plotly.js for offline viewing
- `--max-samples 500` — cap loaded recordings per folder

## Report

The HTML report includes:
- Dataset summary table
- Interactive ECG gallery (overlay / side-by-side / grid)
- Per-metric: score table, per-lead bar chart, PSD overlay (PSD metric), violin plot (DTW)
- Radar chart summarising all metrics
- **Metrics summary table** with Download CSV button
- **Clinical Feature Summary** table (mean ± std, real vs synthetic) — with `--feature-plots`
- **2D feature distribution plots** (scatter + KDE contours) — with `--feature-plots`
- **3D feature distribution plots** (interactive rotation) — with `--feature-plots`
- References / citations

## Running tests

```bash
pytest tests/ -v
```

## Project structure

```
ecgen_eval/
├── data/
│   ├── dataset.py          ECGDataset container
│   └── loader.py           npy / WFDB / CSV loaders
├── features/               Clinical ECG feature extraction (optional: neurokit2)
│   ├── __init__.py         Exports FeatureExtractor, extract_features
│   ├── extractor.py        FeatureExtractor class → (beat_df, summary_df)
│   ├── qrs_detection.py    R-peak detection (neurokit2 primary, scipy fallback)
│   ├── interval_features.py  RR, HR, PR, QRS, QT, QTc, P-wave duration
│   ├── amplitude_features.py ST deviation, T-wave amplitude
│   ├── hrv_features.py     SDNN, RMSSD, pNN50
│   └── utils.py            Bandpass filter, peak helpers
├── metrics/
│   ├── base.py             BaseMetric + MetricResult
│   ├── mmd.py              MMD
│   ├── dtw.py              DTW
│   ├── prd.py              PRD
│   ├── psd.py              PSD divergence
│   ├── fd.py               Fréchet Distance
│   ├── psnr.py             PSNR
│   ├── ssim.py             1-D SSIM
│   ├── swd.py              Sliced Wasserstein Distance
│   ├── mae.py              MAE / RMSE
│   ├── hrv.py              HRV statistics (SDNN, rMSSD, pNN50)
│   ├── pr_dist.py          Distribution Precision & Recall
│   ├── sqi.py              Signal Quality Index
│   ├── nn_dist.py          Nearest-Neighbour Distance
│   ├── heart_rate.py       Heart Rate Distribution
│   └── spectral_entropy.py Spectral Entropy Divergence
├── visualization/
│   ├── ecg_paper.py        ECG graph-paper figure factory
│   ├── ecg_waveform.py     Waveform comparison plots
│   ├── metric_plots.py     Bar, violin, PSD overlay, radar
│   └── feature_plots.py    2D/3D clinical feature distribution plots
├── report/
│   └── html_report.py      HTML report generator
└── cli.py                  Click CLI entry point (eval, visualize, features, list-metrics)
tests/
├── conftest.py
├── test_dataset.py
├── test_loader.py
├── test_metrics.py
└── test_features.py
docs/
└── ecg_features_review.md  Literature review of the 10 clinical features
```
