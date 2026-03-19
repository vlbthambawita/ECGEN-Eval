# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

ECGEN-Eval is a Python package providing evaluation metrics and interactive HTML reports for assessing the quality of synthetically-generated ECG signals. It is part of a broader ECG generation research suite that includes ECGEN-FM, ECGEN-VAE, ECGEN_pulse2pulse_plus, and Pulse2Pulse (all under `/work/vajira/DL2026/`).

## Commands

```bash
# Install
pip install -e ".[dev]"        # core + dev tools
pip install scipy wfdb         # optional: needed for Welch PSD and WFDB loading

# Test
pytest tests/ -v
pytest tests/test_metrics.py::test_mmd -v   # single test
pytest tests/ --cov=ecgen_eval

# Lint / Format
ruff check ecgen_eval/ tests/
black ecgen_eval/ tests/

# CLI
ecgen-eval list-metrics
ecgen-eval eval --real /path/real.npy --synthetic /path/synth.npy --metrics mmd prd psd --output report.html --fs 500
ecgen-eval visualize --real /path/real.npy --synthetic /path/synth.npy --output compare.html
```

## Architecture

**Data flow**: Loader → `ECGDataset` → `BaseMetric.compute()` → `MetricResult` → HTML report

### Data (`ecgen_eval/data/`)
- `ECGDataset`: Core container; holds a numpy array of shape `(N, L, T)` — samples × leads × timepoints — plus metadata (`fs`, `lead_names`, etc.). All metrics and visualization functions accept `ECGDataset` objects.
- `loader.py`: Multi-format loaders (`load_ecg_npy`, `load_ecg_wfdb`, `load_ecg_folder`). `load_ecg_folder` auto-detects format (npy/npz, WFDB, CSV). The CSV loader handles wide, flat, and multi-recording flat layouts via regex-based lead column detection.

### Metrics (`ecgen_eval/metrics/`)
All metrics inherit `BaseMetric` and return a `MetricResult` (scalar score + per-lead scores + extras). The `AVAILABLE_METRICS` dict in `__init__.py` registers all five:

| Key | Class | Approach |
|-----|-------|----------|
| `mmd` | `MMDMetric` | RBF-kernel MMD² on 7 handcrafted signal features per lead |
| `dtw` | `DTWMetric` | Mean DTW distance on randomly sampled pairs; falls back from dtaidistance to pure-NumPy |
| `prd` | `PRDMetric` | Nearest-neighbor PRD%; unpaired, suitable for generative models |
| `psd` | `PSDMetric` | Jensen-Shannon divergence between mean normalized PSDs; uses Welch (scipy) or FFT |
| `fd` | `FrechetMetric` | Fréchet distance between fitted multivariate Gaussians on 11 signal features (FID-like) |

Convention: lower scores are better for all metrics. `MetricResult.higher_is_better` is always `False` here.

### Visualization (`ecgen_eval/visualization/`)
- `ecg_waveform.py`: Plotly interactive comparisons (`overlay`, `sidebyside`, `grid` modes).
- `metric_plots.py`: Per-lead bar, violin, PSD overlay, and radar chart figures.
- `ecg_paper.py`: ECG graph-paper background (5mm/1mm grid) utilities.

### Report (`ecgen_eval/report/html_report.py`)
`generate_report()` produces a single self-contained `.html` file embedding all Plotly figures. Use `plotly_cdn=False` (`--offline` flag) to embed Plotly.js for offline use.

### CLI (`ecgen_eval/cli.py`)
Click-based entry point `ecgen-eval`. Three commands: `eval`, `visualize`, `list-metrics`. `--synthetic` is repeatable to compare multiple models in one report.

## Code Style
- Line length: 100 characters (black + ruff both configured to 100).
- Optional deps (scipy, wfdb) are imported inside functions with `ImportError` fallbacks; maintain this pattern when adding new optional dependencies.
