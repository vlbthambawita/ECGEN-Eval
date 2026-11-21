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
pip install -e ".[biosppy]"    # + biosppy (+ peakutils) for the biosppy feature backend
pip install -e ".[heartpy]"    # + heartpy for the heartpy feature backend
pip install -e ".[umap]"       # + umap-learn for UMAP embedding plots
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
bash docs/diagrams/render.sh   # re-render D2 diagrams (needs d2) after editing docs/diagrams/*.d2
python literature_review_claude/build_db.py   # rebuild docs/literature/ecgen_literature.sqlite + papers.csv from papers_index.csv
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
| `delineation.py` | Per-beat fiducials aligned to the R peaks: QRS onset/offset from all-lead spatial velocity (NumPy/SciPy); P on/offset, T peak (NeuroKit2 `prominence`, every lead, median) and tangent-method T offset |
| `interval_features.py` | RR, HR, PR, QRS, QT, QTc (Bazett), P-wave duration — per beat from fiducials, median over beats; NaN when points are missing (no placeholders) |
| `amplitude_features.py` | ST (J+80 ms) and signed T amplitude per lead vs. PR-segment baseline (averaged across leads in summary) |
| `hrv_features.py` | SDNN, RMSSD, pNN50 from RR series |
| `backends.py` | Delineation backends (`hybrid` default, `neurokit2`, `scipy`, `biosppy`, `heartpy` R peaks only): recording → `(rpeaks, waves)`; registry `AVAILABLE_BACKENDS` + `register_backend`; backends declare `rpeak_methods` / `delineation_methods`, which `get_backend` validates |
| `groups.py` | Feature groups (`rhythm`, `intervals`, `hrv`, `amplitude`) computed from a `RecordingContext`; registry `AVAILABLE_FEATURE_GROUPS` + `register_feature_group` / `@feature_group`; `resolve_features` handles group/column/callable selection |
| `extractor.py` | `FeatureExtractor(features=..., backend=...)`: takes `ECGDataset`, returns `(beat_df, summary_df)` |

Two independent choices: `features=` (what to compute) and `backend=` (which library delineates). The default (`hybrid`, all groups) reproduces the pre-backend output exactly.

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
| `psnr` | `PSNRMetric` | Nearest-neighbour PSNR (dB) |
| `ssim` | `SSIMMetric` | Global 1-D SSIM to nearest synthetic neighbour |
| `swd` | `SWDMetric` | Sliced Wasserstein distance on the 7 MMD features |
| `mae` | `MAEMetric` | Nearest-neighbour MAE (RMSE in `extra`) |
| `hrv` | `HRVMetric` | Mean JS divergence of SDNN / rMSSD / pNN50 distributions |
| `pr_dist` | `PRDistMetric` | k-NN precision & recall; score is their F-score |
| `sqi` | `SQIMetric` | Correlation of synthetic signals with a real-data template |
| `nn_dist` | `NNDistMetric` | Nearest-neighbour distance; authenticity (memorisation) in `extra` |
| `heart_rate` | `HeartRateMetric` | JS divergence of heart-rate distributions |
| `spectral_entropy` | `SpectralEntropyMetric` | JS divergence of spectral-entropy distributions |
| `mse` / `rmse` | `MSEMetric` / `RMSEMetric` | Pointwise MSE / RMSE on matched pairs (`pairing`) |
| `euclidean` | `EuclideanMetric` | Time-domain L2 distance on matched pairs (= √T · RMSE) |
| `pearson` | `PearsonMetric` | Pearson r on matched pairs; optional max cross-correlation within a lag |
| `cosine` | `CosineMetric` | Cosine similarity on matched pairs |
| `curve_frechet` | `CurveFrechetMetric` | Discrete (curve) Fréchet distance on matched, decimated pairs; unrelated to `fd`/`fed` |
| `js_div` | `AmplitudeJSMetric` | JS divergence of pooled amplitude histograms (KL in `extra`) |
| `ks_test` | `KSTestMetric` | Mean two-sample KS statistic over the 7 MMD features; p-values in `extra` |
| `c2st` | `C2STMetric` | Classifier two-sample test: max(0, CV accuracy − 0.5) of a real-vs-synthetic classifier |

`FEDMetric` supports three backbones (selected via `--backbone`): `ecgfounder` (PKUDigitalHealth/ECGFounder, RegNet, 10.7 M ECGs), `hubert_ecg` (Edoardo-BS/hubert-ecg-base, Transformer, 9.1 M ECGs), `ecgfm` (bowang-lab/ECG-FM, wav2vec2-style, 1.5 M ECGs). Weights are downloaded from HuggingFace **on first use** and cached locally. Set `HF_HOME` to control the cache directory.

The shared Fréchet math lives in `ecgen_eval/metrics/_frechet_utils.py` (used by both `fd.py` and `fed.py`). Encoder adapters live in `ecgen_eval/metrics/encoders/` — add new backbones there without touching `FEDMetric`.

Shared private helpers in `ecgen_eval/metrics/` — reuse them instead of copying code:
- `_matching.py`: subsampling and the `pairing` protocols (`nn` nearest neighbour, `paired` index-aligned, `mean` mean waveforms), `split_half` for real-vs-real baselines.
- `_pairwise.py`: `PairwiseSignalMetric`, base class of `mse`, `rmse`, `euclidean`, `pearson`, `cosine`, `curve_frechet`. Subclasses implement `_pair_values(R, S)`; the base handles pairing, the baseline (`extra["real_vs_real"]`) and common extras.
- `_signal_features.py` (7- and 11-feature descriptors), `_divergence.py` (JS / KL), `_stats.py` (KS test, p-value adjustment, Cohen's d).

Existing metric scores are pinned in `tests/test_metrics.py::test_original_metric_scores_unchanged`; a refactor of the helpers must keep them.

Convention: lower is better unless the metric sets `higher_is_better = True` (`psnr`, `ssim`, `pr_dist`, `sqi`, `pearson`, `cosine`).

CLI `eval` runs a curated set of 12 metrics by default (`DEFAULT_METRICS` in `cli.py`: `fd`, `mmd`, `pr_dist`, `c2st`, `rmse`, `pearson`, `dtw`, `js_div`, `psd`, `heart_rate`, `hrv`, `nn_dist`); `-m all` expands to every metric except `fed` (`ALL_METRICS`), which must always be named explicitly. A new metric is not in the default unless added to `DEFAULT_METRICS`. `eval` passes the real dataset's `fs` to any metric whose constructor takes `fs`, and `--pairing` to any whose constructor takes `pairing`. Metric constructors must be callable with no arguments.

### Visualization (`ecgen_eval/visualization/`)
- `ecg_waveform.py`: Plotly interactive comparisons (`overlay`, `sidebyside`, `grid` modes); `show_r_peaks=True` marks detected R peaks.
- `metric_plots.py`: Per-lead bar, violin, PSD overlay, amplitude-histogram overlay (`js_div`), and radar chart figures.
- `beat_plots.py`: `plot_beat_bands` (median + quantile band, or density map, of all R-peak-aligned beats) and `extract_aligned_beats`.
- `embedding_plots.py`: `compute_embedding_2d` / `plot_embedding_2d` — PCA, t-SNE, UMAP (`[umap]` extra); PCA and UMAP are fitted on the real data only.
- `ecg_paper.py`: ECG graph-paper background (5mm/1mm grid) utilities.
- `feature_plots.py`: 2D and 3D clinical feature distribution plots.
  - `plot_feature_2d(real_df, synth_df, x, y)` — scatter + `Histogram2dContour` KDE overlay.
  - `plot_feature_pair_grid(real_df, synth_df, pairs)` — subplots grid; defaults to `DEFAULT_2D_PAIRS`.
  - `plot_feature_3d(real_df, synth_df, x, y, z)` — interactive `Scatter3d`.
  - `plot_feature_triple_grid(real_df, synth_df, triples)` — multi-scene 3D grid; defaults to `DEFAULT_3D_TRIPLES`.

### Report (`ecgen_eval/report/html_report.py`)
`generate_report()` produces a single self-contained `.html` file embedding all Plotly figures. Use `plotly_cdn=False` (`--offline` flag) to embed Plotly.js for offline use.

New optional parameters: `feature_df_real`, `feature_dfs_synth`, `feature_plots_2d`, `feature_plots_3d` — when provided, add a Clinical Feature Summary table (with KS statistics from `ecgen_eval.features.stats.compare_feature_distributions`) and 2D/3D distribution plot sections to the report.

Further report options: `beat_bands` (Beat Morphology section, on by default), `embedding_plots` (list of figures), `gallery_selection` (`first` / `random`). Metric score tables show scalar extras listed in `_EXTRA_COLUMNS` (real-vs-real baseline, accuracy, AUC, KL).

### CLI (`ecgen_eval/cli.py`)
Click-based entry point `ecgen-eval`. Five commands:
- `eval` — run metrics + generate report; `--feature-plots` triggers feature extraction and adds plot sections; `--pairing`, `--embedding-plots` / `--embedding-method` / `--embedding-features`, `--no-beat-bands`, `--gallery-selection`.
- `features` — extract clinical features only and save a summary CSV; `--stats-output` writes two-sample tests per feature.
- `visualize` — ECG waveform comparison plots, no metrics; `--compare-mode beats|beat-density`, `--show-r-peaks`, `--embedding`.
- `list-metrics` — print available metric registry.
- `list-features` — print feature groups and extraction backends.

`--synthetic` is repeatable in `eval` and `features` to compare multiple models in one run.

### Docs for a metric
Each metric has a page `docs/metrics/<key>.md` (with an interactive demo from `docs/javascripts/metric-viz.js`), a section in `docs/user-guide/metric-reference.md`, rows in `docs/user-guide/metrics.md`, `docs/metrics/index.md`, `docs/references.md` and the README, an entry in `docs/api/metrics.md` and `mkdocs.yml`, and its key in the `METRICS` table of `literature_review_claude/build_db.py` (then rebuild the DB). `METRIC_KEYS` in `docs/javascripts/literature-db.js` turns keys into links.

## Code Style
- Line length: 100 characters (black + ruff both configured to 100).
- Optional deps (scipy, wfdb) are imported inside functions with `ImportError` fallbacks; maintain this pattern when adding new optional dependencies.
