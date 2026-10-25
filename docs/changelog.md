# Changelog

All notable changes to ECGEN-Eval are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/). Releases are published to
[PyPI](https://pypi.org/project/ecgen-eval/) from `v*` tags.

You are reading the documentation for **v{{ ecgen_version }}**. Check your installed
version with `ecgen-eval --version` or `python -c "import ecgen_eval; print(ecgen_eval.__version__)"`.

## [Unreleased]

### Added

- Documentation site (MkDocs Material + mkdocstrings) with a user guide, metric reference,
  development guides and an API reference, deployed to GitHub Pages from `main`.
- Architecture and pipeline diagrams written in [D2](https://d2lang.com), with light and
  dark variants.
- `docs` optional dependency group: `pip install -e ".[docs]"`.
- Version badge in the documentation header and footer.
- Literature Review section in the docs: a summary of how synthetic ECGs are evaluated
  (Oct 2023 – Oct 2026) and an interactive Paper Database with filters for category, year,
  evaluation category, metric, loss function, task, conditioning, data type, data format,
  leads, sampling rate, segment length, dataset, data access, code and publication type; a
  "Metrics by evaluation category" view (Fidelity, Diversity, Utility, Privacy, Fairness,
  Robustness, Clinical validity, Human / expert, Conditional consistency, Efficiency) listing
  each metric family with the papers that use it; and a SQL console. The SQLite database
  (`docs/literature/ecgen_literature.sqlite`) is built by `literature_review_claude/build_db.py`
  from the review index and per-metric records in `structured_extraction.jsonl`.

### Changed

- **`ecgen-eval eval` no longer runs `fed` by default.** Without `-m`, every metric except
  `fed` runs, so a plain run doesn't need PyTorch or download model weights. Use `-m fed`
  to include it.
- `ecgen-eval eval` passes the real dataset's sampling rate to metrics that take one (`psd`,
  `spectral_entropy`, `hrv`, `heart_rate`) and to the report. It also warns when a synthetic
  dataset's sampling rate differs from the real one.

### Fixed

- `--fs` was ignored by `psd`, `spectral_entropy`, `hrv` and `heart_rate`, which always
  assumed 500 Hz.
- `prd` built an `(N_real, N_synth, L·T)` array and could need ~60 GB at default settings.
  It now uses under 1 GB with identical results.
- `ecgen_eval.__version__` and `ecgen-eval --version` always reported `0.1.0`. They now report
  the installed package version.
- `hrv` docstring now describes the actual score (mean JS divergence of SDNN, rMSSD and pNN50).
- README examples used `--metrics a b c`, which fails; the option must be repeated
  (`-m a -m b -m c`).

## [0.5.0] — 2026-04-06

### Added

- **Fréchet ECG Distance (`fed`)** — FID-style metric on embeddings from pre-trained ECG
  foundation models, with three backbones:
  `ecgfounder` (ECGFounder), `hubert_ecg` (HuBERT-ECG) and `ecgfm` (ECG-FM).
  Weights are downloaded from the Hugging Face Hub on first use.
- Encoder adapters in `ecgen_eval.metrics.encoders` with a `get_encoder()` factory.
- CLI options `--backbone`, `--fed-device` and `--fed-batch-size`.
- `fed` optional dependency group (`torch`, `transformers`, `huggingface_hub`).

### Changed

- Fréchet-distance math moved to `ecgen_eval.metrics._frechet_utils` and shared by `fd` and `fed`.

## [0.4.0] — 2026-03-19

Maintenance release with no library changes (refreshed example report).

## [0.3.0] — 2026-03-19

### Added

- **Clinical feature extraction** (`ecgen_eval.features`): RR, heart rate, PR, QRS, QT,
  QTc (Bazett), P-wave duration, ST deviation, T-wave amplitude and HRV (SDNN, RMSSD, pNN50),
  using NeuroKit2 with a SciPy fallback.
- `FeatureExtractor` / `extract_features` returning `beat_df` and `summary_df`.
- 2D and 3D feature distribution plots (`plot_feature_2d`, `plot_feature_pair_grid`,
  `plot_feature_3d`, `plot_feature_triple_grid`, `plot_feature_2d_multi`).
- `ecgen-eval features` command and `ecgen-eval eval --feature-plots`.
- Clinical Feature Summary table and 2D/3D sections in the HTML report.
- `features` optional dependency group (`neurokit2`, `scipy`).
- [ECG Feature Review](ecg_features_review.md) document.

## [0.2.0] — 2026-03-19

### Added

- Ten new metrics: `psnr`, `ssim`, `swd`, `mae`, `hrv`, `pr_dist`, `sqi`, `nn_dist`,
  `heart_rate` and `spectral_entropy`.
- Metrics summary table with CSV download in the HTML report.
- Automated PyPI publishing (Trusted Publishing) from `v*` tags.

### Changed

- Package version is derived from git tags (`hatch-vcs`).

## [0.1.0] — 2026-03-19

Initial release.

- `ECGDataset` container and loaders for NumPy, WFDB and CSV (`load_ecg_npy`,
  `load_ecg_wfdb`, `load_ecg_folder`).
- Metrics: `mmd`, `dtw`, `prd`, `psd`, `fd`.
- Interactive Plotly visualizations on ECG graph paper and a self-contained HTML report.
- `ecgen-eval` CLI with `eval`, `visualize` and `list-metrics`.

[Unreleased]: https://github.com/vlbthambawita/ECGEN-Eval/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/vlbthambawita/ECGEN-Eval/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/vlbthambawita/ECGEN-Eval/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/vlbthambawita/ECGEN-Eval/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/vlbthambawita/ECGEN-Eval/releases/tag/v0.2.0
[0.1.0]: https://pypi.org/project/ecgen-eval/0.1.0/
