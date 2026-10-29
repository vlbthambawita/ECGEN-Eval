# Changelog

All notable changes to ECGEN-Eval are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/). Releases are published to
[PyPI](https://pypi.org/project/ecgen-eval/) from `v*` tags.

You are reading the documentation for **v{{ ecgen_version }}**. Check your installed
version with `ecgen-eval --version` or `python -c "import ecgen_eval; print(ecgen_eval.__version__)"`.

## [Unreleased]

## [0.8.0] — 2026-10-29

Same code as 0.7.1, released under a minor version because 0.7.1 added new features
(selectable clinical features and extraction backends, see below). Prefer 0.8.0 over 0.7.1.

## [0.7.1] — 2026-10-29

### Added

- **Selectable clinical features.** `FeatureExtractor(features=...)` / `extract_features(...,
  features=...)` take feature group names (`rhythm`, `intervals`, `hrv`, `amplitude`), single
  column names, `FeatureGroup` instances or `func(ctx) -> dict` callables. Custom groups can be
  registered with `register_feature_group` or the `@feature_group` decorator.
- **Selectable extraction library.** `FeatureExtractor(backend=...)` chooses how beats are
  delineated: `hybrid` (default, unchanged results), `neurokit2` (plain `nk.ecg_delineate` with
  `dwt`/`cwt`/`peak`/`prominence`) or `scipy` (no NeuroKit2). Custom backends subclass
  `DelineationBackend` and are registered with `register_backend`. `rpeak_method="scipy"`
  forces the SciPy R-peak detector.
- CLI: `-F/--feature`, `--feature-backend`, `--rpeak-method` and `--delineation-method` for
  `features` and `eval --feature-plots`; new `list-features` command.

### Changed

- Default extraction (`hybrid` backend, all feature groups) gives exactly the same output as
  v0.7.0. `FeatureExtractor(rpeak_method=..., delineation_method=...)` now default to `None`
  (the backend's own default).
- Docs: feature-extraction and architecture diagrams show the backend → feature-group
  pipeline; new *Choosing features and libraries* section in Clinical Features.

## [0.7.0] — 2026-10-29

### Fixed

- **Clinical feature extractor.** In v0.6.0 and earlier:
    - PR, QT, QTc, P-wave duration and ST deviation were always `NaN` with NeuroKit2
      installed, because the `peak` delineation method never returns the wave boundaries
      they need;
    - fixed placeholder values were returned without NeuroKit2;
    - QRS duration was measured from the Q dip to the S dip.

  Delineation now uses all leads (new module `ecgen_eval.features.delineation`):
    - QRS onset/offset from the spatial velocity (sum of absolute slopes of all leads);
    - P boundaries and T peaks from NeuroKit2's `prominence` method on every lead, combined
      with the median across leads;
    - tangent-method T offset.

  Intervals are measured per beat and summarised with the median over beats. ST is read at
  J + 80 ms and T is the signed extreme, both against the PR-segment baseline. Validation
  on 500 held-out PTB-XL records against GE 12SL (PTB-XL+):
    - QRS: MAE 6.4 ms, r 0.88;
    - PR: MAE 8.5 ms, r 0.87;
    - QT: r 0.85, about 17 ms shorter on average;
    - P-wave duration: MAE 12 ms, r 0.41 (GE 12SL vs Philips Uni-G: r 0.48);
    - T amplitude: r 0.96;
    - ST vs Uni-G at J + 80 ms: r 0.97.

  Features that cannot be measured are `NaN`, never placeholders. Without NeuroKit2,
  heart rate, HRV, QRS, ST and T amplitude are still measured.
- R peaks for the clinical features are detected on the `nk.ecg_clean()`-filtered signal.
  Heart-rate error against 12SL drops from 2.4 to 1.7 bpm.

### Changed

- **Feature values differ from v0.6.0.** Re-extract features saved with earlier versions
  before comparing them with new results.
- `beat_df` gains per-beat `pr_interval_ms`, `qrs_duration_ms`, `qt_interval_ms` and
  `p_wave_duration_ms` columns. ST and T amplitude are now medians over beats.

### Added

- `FeatureExtractor(delineation_method=...)` selects the NeuroKit2 method for the P and T
  waves (default `"prominence"`).
- "Clinical Features Explained" docs section. It explains every clinical feature for
  non-clinical readers, with an interactive heartbeat anatomy (the electrical wave through
  the heart), one interactive widget per feature, typical ranges, and a validation table
  against commercial ECG software.
- Catalogue of 43 open-source ECG feature extractors usable from Python, checked against
  their source code. For each tool it records the accepted inputs, sampling-rate handling,
  minimum duration and native output names, mapped to a 94-feature vocabulary. It is
  available as a "Feature extractors" tab in the Paper Database, as new SQLite tables
  (`extractors`, `extractor_inputs`, `extractor_features`, `feature_vocab`, views
  `feature_coverage` and `ecgen_feature_support`), and as CSV exports. The literature
  review adds `04_ecg_feature_extractors.md`.
- The Metric Reference page links each metric to its explanation, API entry, source file
  and papers.

### Docs

- Fixed citations: the Zigel et al. PRD paper DOI, and the SSIM reference (now Shahriari et
  al., IEEE TBME 2018).

## [0.6.0] — 2026-10-28

### Added

- Documentation site (MkDocs Material + mkdocstrings) with a user guide, metric reference,
  development guides and an API reference, deployed to GitHub Pages from `main`.
- Architecture and pipeline diagrams written in [D2](https://d2lang.com), with light and
  dark variants.
- `docs` optional dependency group: `pip install -e ".[docs]"`.
- Version badge in the documentation header and footer.
- "Metrics Explained" docs section: one page per metric (all 16) with an interactive
  visualization (sliders and presets on simulated data, scored with the same formulas as the
  package), a step-by-step description of the implementation, the maths, guidance on reading
  the score, and CLI / Python usage. Built with `docs/javascripts/metric-viz.js`, no extra
  dependencies. The former User Guide FED page (backbones, weight caching, encoders) is
  merged into the FED page there.
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

- **`heart_rate` and `hrv` R-peak detection.** The old detector (amplitude threshold of
  mean + 0.5·std, peaks ≥ 0.5 s apart) could not measure heart rates above 120 bpm and often
  counted T waves as beats or missed small or inverted QRS complexes. A new slope-energy QRS
  detector (Pan–Tompkins style, 0.2 s refractory period, up to 300 bpm) is shared by both
  metrics. On held-out PTB-XL records it matches the GE 12SL heart rate within 5 bpm for 91 %
  of lead recordings, up from 48 %. Scores of `heart_rate` and `hrv` change accordingly.
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

[Unreleased]: https://github.com/vlbthambawita/ECGEN-Eval/compare/v0.8.0...HEAD
[0.8.0]: https://github.com/vlbthambawita/ECGEN-Eval/compare/v0.7.1...v0.8.0
[0.7.1]: https://github.com/vlbthambawita/ECGEN-Eval/compare/v0.7.0...v0.7.1
[0.7.0]: https://github.com/vlbthambawita/ECGEN-Eval/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/vlbthambawita/ECGEN-Eval/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/vlbthambawita/ECGEN-Eval/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/vlbthambawita/ECGEN-Eval/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/vlbthambawita/ECGEN-Eval/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/vlbthambawita/ECGEN-Eval/releases/tag/v0.2.0
[0.1.0]: https://pypi.org/project/ecgen-eval/0.1.0/
