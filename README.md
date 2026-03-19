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
pip install scipy          # for Welch PSD and resampling (recommended)
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

| Key | Name | Description |
|---|---|---|
| `mmd` | Maximum Mean Discrepancy | Distribution distance in feature space |
| `dtw` | Dynamic Time Warping | Morphological shape similarity |
| `prd` | Percent Root-mean-square Difference | Waveform distortion (nearest-neighbour) |
| `psd` | PSD Divergence | JS divergence between mean power spectra |
| `fd` | Fréchet Distance | FID-like distance in 11-feature embedding |

All metrics return a `MetricResult` with `.score`, `.per_lead_scores`, and `.extra`.

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
- `--metrics mmd prd psd` — run a subset of metrics
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
│   └── fd.py           Fréchet Distance
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
