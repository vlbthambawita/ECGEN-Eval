# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

ECGEN-Eval is a Python package providing evaluation metrics and interactive HTML reports for assessing the quality of synthetically-generated ECG signals. It is part of a broader ECG generation research suite that includes ECGEN-FM, ECGEN-VAE, ECGEN_pulse2pulse_plus, and Pulse2Pulse (all under `/work/vajira/DL2026/`).

## Commands

```bash
# Install
pip install -e ".[dev]"        # core + dev tools
pip install -e ".[features]"   # + neurokit2 + scipy for clinical feature extraction
pip install -e ".[fed]"        # + torch + transformers + huggingface_hub for FED metric
pip install scipy wfdb         # optional: needed for Welch PSD and WFDB loading

# Test
pytest tests/ -v
pytest tests/test_metrics.py::test_mmd -v   # single test
pytest tests/test_features.py -v            # feature extraction tests
pytest tests/ --cov=ecgen_eval

# Lint / Format
ruff check ecgen_eval/ tests/
black ecgen_eval/ tests/

# CLI
ecgen-eval list-metrics
ecgen-eval eval --real /path/real.npy --synthetic /path/synth.npy -m mmd -m prd -m psd --output report.html --fs 500   # -m is repeatable
ecgen-eval eval --real /path/real.npy --synthetic /path/synth.npy --metrics fed --backbone ecgfounder --fed-device cpu --output report.html
ecgen-eval eval --real /path/real.npy --synthetic /path/synth.npy --feature-plots --output report.html
ecgen-eval features --real /path/real.npy --synthetic /path/synth.npy --output features.csv
ecgen-eval visualize --real /path/real.npy --synthetic /path/synth.npy --output compare.html

# Docs (MkDocs Material + mkdocstrings; deployed to GitHub Pages by .github/workflows/docs.yml)
pip install -e ".[docs]"
mkdocs serve
mkdocs build --strict
```

## Architecture

**Data flow**: Loader → `ECGDataset` → `BaseMetric.compute()` → `MetricResult` → HTML report

**Feature flow**: `ECGDataset` → `FeatureExtractor.extract()` → `(beat_df, summary_df)` → 2D/3D plots → HTML report

### Data (`ecgen_eval/data/`)
- `ECGDataset`: Core container; holds a numpy array of shape `(N, L, T)` — samples × leads × timepoints — plus metadata (`fs`, `lead_names`, etc.). All metrics and visualization functions accept `ECGDataset` objects.
- `loader.py`: Multi-format loaders (`load_ecg_npy`, `load_ecg_wfdb`, `load_ecg_folder`). `load_ecg_folder` auto-detects format (npy/npz, WFDB, CSV). The CSV loader handles wide, flat, and multi-recording flat layouts via regex-based lead column detection.

### Features (`ecgen_eval/features/`)
Optional subpackage (requires `neurokit2`; falls back to scipy/NumPy). Extracts 10 clinical ECG features per recording into a `pandas.DataFrame`.

| Module | Purpose |
|--------|---------|
| `qrs_detection.py` | R-peak detection via `nk.ecg_peaks()` (Pan-Tompkins); scipy fallback |
| `interval_features.py` | RR, HR, PR, QRS, QT, QTc (Bazett), P-wave duration |
| `amplitude_features.py` | ST deviation and T-wave amplitude per lead (averaged across leads in summary) |
| `hrv_features.py` | SDNN, RMSSD, pNN50 from RR series |
| `extractor.py` | `FeatureExtractor` class: takes `ECGDataset`, returns `(beat_df, summary_df)` |

`beat_df` has one row per (recording, beat, lead). `summary_df` has one row per recording with aggregated feature values — used directly in 2D/3D distribution plots.

Key column names in `summary_df` (used by default plot pairs/triples):
`rr_mean_ms`, `hr_bpm`, `pr_interval_ms`, `qrs_duration_ms`, `qt_interval_ms`, `qtc_bazett_ms`, `st_deviation_mv`, `t_amplitude_mv`, `p_wave_duration_ms`, `hrv_sdnn_ms`, `hrv_rmssd_ms`, `hrv_pnn50`.

### Metrics (`ecgen_eval/metrics/`)
All metrics inherit `BaseMetric` and return a `MetricResult` (scalar score + per-lead scores + extras). The `AVAILABLE_METRICS` dict in `__init__.py` registers all metrics:

| Key | Class | Approach |
|-----|-------|----------|
| `mmd` | `MMDMetric` | RBF-kernel MMD² on 7 handcrafted signal features per lead |
| `dtw` | `DTWMetric` | Mean DTW distance on randomly sampled pairs; falls back from dtaidistance to pure-NumPy |
| `prd` | `PRDMetric` | Nearest-neighbor PRD%; unpaired, suitable for generative models |
| `psd` | `PSDMetric` | Jensen-Shannon divergence between mean normalized PSDs; uses Welch (scipy) or FFT |
| `fd` | `FDMetric` | Fréchet distance between fitted multivariate Gaussians on 11 handcrafted signal features (FID-like) |
| `fed` | `FEDMetric` | Fréchet ECG Distance using deep embeddings from a pre-trained foundation model (requires `[fed]` extras) |

`FEDMetric` supports three backbones (selected via `--backbone`): `ecgfounder` (PKUDigitalHealth/ECGFounder, RegNet, 10.7 M ECGs), `hubert_ecg` (Edoardo-BS/hubert-ecg-base, Transformer, 9.1 M ECGs), `ecgfm` (bowang-lab/ECG-FM, wav2vec2-style, 1.5 M ECGs). Weights are downloaded from HuggingFace **on first use** and cached locally. Set `HF_HOME` to control the cache directory.

The shared Fréchet math lives in `ecgen_eval/metrics/_frechet_utils.py` (used by both `fd.py` and `fed.py`). Encoder adapters live in `ecgen_eval/metrics/encoders/` — add new backbones there without touching `FEDMetric`.

Convention: lower scores are better for all metrics. `MetricResult.higher_is_better` is always `False` here.

### Visualization (`ecgen_eval/visualization/`)
- `ecg_waveform.py`: Plotly interactive comparisons (`overlay`, `sidebyside`, `grid` modes).
- `metric_plots.py`: Per-lead bar, violin, PSD overlay, and radar chart figures.
- `ecg_paper.py`: ECG graph-paper background (5mm/1mm grid) utilities.
- `feature_plots.py`: 2D and 3D clinical feature distribution plots.
  - `plot_feature_2d(real_df, synth_df, x, y)` — scatter + `Histogram2dContour` KDE overlay.
  - `plot_feature_pair_grid(real_df, synth_df, pairs)` — subplots grid; defaults to `DEFAULT_2D_PAIRS`.
  - `plot_feature_3d(real_df, synth_df, x, y, z)` — interactive `Scatter3d`.
  - `plot_feature_triple_grid(real_df, synth_df, triples)` — multi-scene 3D grid; defaults to `DEFAULT_3D_TRIPLES`.

### Report (`ecgen_eval/report/html_report.py`)
`generate_report()` produces a single self-contained `.html` file embedding all Plotly figures. Use `plotly_cdn=False` (`--offline` flag) to embed Plotly.js for offline use.

New optional parameters: `feature_df_real`, `feature_dfs_synth`, `feature_plots_2d`, `feature_plots_3d` — when provided, add a Clinical Feature Summary table and 2D/3D distribution plot sections to the report.

### CLI (`ecgen_eval/cli.py`)
Click-based entry point `ecgen-eval`. Four commands:
- `eval` — run metrics + generate report; `--feature-plots` triggers feature extraction and adds plot sections.
- `features` — extract clinical features only and save a summary CSV.
- `visualize` — ECG waveform comparison plots, no metrics.
- `list-metrics` — print available metric registry.

`--synthetic` is repeatable in `eval` and `features` to compare multiple models in one run.

## Code Style
- Line length: 100 characters (black + ruff both configured to 100).
- Optional deps (scipy, wfdb) are imported inside functions with `ImportError` fallbacks; maintain this pattern when adding new optional dependencies.
