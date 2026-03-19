# ECGEN-Eval

Evaluation metrics and interactive HTML reports for synthetic ECG quality assessment.
Part of the ECGEN research suite (ECGEN-FM, ECGEN-VAE, Pulse2Pulse).

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

## CLI

```bash
# Run all metrics and generate interactive HTML report
ecgen-eval eval \
  --real   /path/to/real_ecgs.npy \
  --synthetic /path/to/model1_ecgs.npy \
  --synthetic /path/to/model2_ecgs.npy \
  --output report.html

# List available metrics
ecgen-eval list-metrics

# ECG waveform comparison only (no metrics)
ecgen-eval visualize \
  --real /path/to/real.npy \
  --synthetic /path/to/synth.npy \
  --compare-mode overlay
```

Key options for `eval`:
- `--metrics mmd prd psd psnr hrv` — run a subset of metrics
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
- References / citations

## Running tests

```bash
pytest tests/ -v
```

## Project structure

```
ecgen_eval/
├── data/
│   ├── dataset.py      ECGDataset container
│   └── loader.py       npy / WFDB / CSV loaders
├── metrics/
│   ├── base.py         BaseMetric + MetricResult
│   ├── mmd.py          MMD
│   ├── dtw.py          DTW
│   ├── prd.py          PRD
│   ├── psd.py          PSD divergence
│   ├── fd.py           Fréchet Distance
│   ├── psnr.py         PSNR
│   ├── ssim.py         1-D SSIM
│   ├── swd.py          Sliced Wasserstein Distance
│   ├── mae.py          MAE / RMSE
│   ├── hrv.py          HRV statistics (SDNN, rMSSD, pNN50)
│   ├── pr_dist.py      Distribution Precision & Recall
│   ├── sqi.py          Signal Quality Index
│   ├── nn_dist.py      Nearest-Neighbour Distance
│   ├── heart_rate.py   Heart Rate Distribution
│   └── spectral_entropy.py  Spectral Entropy Divergence
├── visualization/
│   ├── ecg_paper.py    ECG graph-paper figure factory
│   ├── ecg_waveform.py Waveform comparison plots
│   └── metric_plots.py Bar, violin, PSD overlay, radar
├── report/
│   └── html_report.py  HTML report generator
└── cli.py              Click CLI entry point
tests/
├── conftest.py
├── test_dataset.py
├── test_loader.py
└── test_metrics.py
```
