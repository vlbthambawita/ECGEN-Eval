# ECGEN-Eval — Task Backlog

## Status Legend
- [ ] Not started
- [~] In progress
- [x] Done

---

## 1. Clinically Valuable ECG Feature Extraction

### 1.1 Literature Review — Top 10 Clinical ECG Features
Do a targeted review to confirm the most clinically and diagnostically important ECG features.
Priority candidates (from cardiology literature and established guidelines):

| # | Feature | Description | Clinical Relevance |
|---|---------|-------------|-------------------|
| 1 | **RR interval** | Peak-to-peak interval between consecutive R-waves | Heart rate, rhythm regularity, arrhythmia detection |
| 2 | **Heart Rate (HR)** | 60 / mean(RR) in bpm | Bradycardia / tachycardia |
| 3 | **PR interval** | Onset of P-wave to onset of QRS | AV conduction; prolonged → 1st-degree AV block |
| 4 | **QRS duration** | Onset to offset of QRS complex | Bundle branch blocks, ventricular conduction |
| 5 | **QT interval** | Onset of QRS to end of T-wave | Long-QT syndrome, drug effects |
| 6 | **QTc (corrected QT)** | QT / sqrt(RR) [Bazett] or QT / RR^(1/3) [Fridericia] | Rate-independent arrhythmia risk marker |
| 7 | **ST deviation** | Mean ST segment voltage relative to isoelectric line | Ischemia / myocardial infarction |
| 8 | **T-wave amplitude** | Signed peak T-wave amplitude per lead | Hyperkalemia, ischemia, LVH |
| 9 | **P-wave duration** | Width of P-wave | Atrial enlargement, AF risk |
| 10 | **HRV — SDNN / RMSSD** | Std-dev and RMS of successive RR differences | Autonomic tone, cardiac risk stratification |

**References to check:** PhysioNet documentation, AHA/ACC ECG guidelines, NeuroKit2 paper (Makowski et al. 2021), WFDB Python docs.

**Deliverable:** `docs/ecg_features_review.md` summarising chosen features with references.

---

### 1.2 Implement Feature Extractor (`ecgen_eval/features/`)

Build a dedicated `features` subpackage using well-known, validated algorithms.

**Design:**
```
ecgen_eval/features/
    __init__.py          # exports FeatureExtractor, extract_features
    extractor.py         # FeatureExtractor class: accepts ECGDataset, returns DataFrame
    qrs_detection.py     # R-peak detection (Pan-Tompkins via NeuroKit2 or scipy)
    interval_features.py # RR, HR, PR, QRS, QT, QTc, P-wave duration
    amplitude_features.py# ST deviation, T-wave amplitude
    hrv_features.py      # SDNN, RMSSD, pNN50 from RR series
    utils.py             # shared delineation helpers
```

**Algorithm choices (prefer well-cited, open-source):**
- R-peak detection: `neurokit2.ecg_peaks()` (Pan-Tompkins) — primary; fall back to `scipy` zero-crossing if neurokit2 not installed.
- Full delineation (P, QRS, T boundaries): `neurokit2.ecg_delineate()`.
- HRV: `neurokit2.hrv_time()` or manual from RR array.

**Output:** `pandas.DataFrame` with shape `(N_beats × N_leads, N_features)` and a per-recording summary DataFrame with mean/std per feature.

**Tasks:**
- [x] Add `neurokit2` as optional dependency in `pyproject.toml` (extras: `[features]`)
- [x] Implement `qrs_detection.py` with Pan-Tompkins primary + scipy fallback
- [x] Implement `interval_features.py` (RR, HR, PR, QRS, QT, QTc)
- [x] Implement `amplitude_features.py` (ST deviation, T-wave amplitude per lead)
- [x] Implement `hrv_features.py` (SDNN, RMSSD, pNN50)
- [x] Implement `FeatureExtractor` class wiring all of the above
- [x] Add `extract_features` convenience function
- [x] Write unit tests in `tests/test_features.py` using synthetic sinusoidal data
- [x] Add CLI command: `ecgen-eval features --real /path/real.npy --synthetic /path/synth.npy --output features.csv`

---

## 2. Distribution Comparison Plots (2D)

Compare per-feature distributions between real and synthetic ECGs using joint/marginal scatter plots.

**Goal:** For any pair of features (e.g. RR vs HR, QRS vs QT, ST vs T-amplitude) show where real and synthetic clouds overlap or diverge.

**Implementation:** `ecgen_eval/visualization/feature_plots.py`

**Plot types:**
- **2D KDE overlay** — kernel density contours for real (blue) and synthetic (orange) on the same axes.
- **Marginal scatter** — joint scatter with marginal histograms (seaborn `jointplot`-style, implemented in Plotly for self-contained HTML output).
- **Feature pair grid** — configurable list of `(feature_x, feature_y)` pairs, one subplot per pair.

**Tasks:**
- [x] Implement `plot_feature_2d(real_df, synth_df, x_feature, y_feature)` → Plotly Figure
- [x] Implement `plot_feature_pair_grid(real_df, synth_df, pairs)` → Plotly Figure (subplots)
- [x] Add 2D plots to `generate_report()` (new section: "Clinical Feature Distributions")
- [x] Add CLI flag: `ecgen-eval eval --feature-plots` to enable section
- [x] Tests: smoke-test that figures are returned without error

**Example pairs to include by default:**
```python
DEFAULT_2D_PAIRS = [
    ("rr_mean_ms", "hr_bpm"),
    ("qrs_duration_ms", "qt_interval_ms"),
    ("st_deviation_mv", "t_amplitude_mv"),
    ("rr_mean_ms", "hrv_sdnn_ms"),
]
```

---

## 3. Distribution Comparison Plots (3D)

Extend 2D comparisons to three features simultaneously.

**Implementation:** `ecgen_eval/visualization/feature_plots.py` (extend existing module)

**Plot types:**
- **3D scatter** — Plotly `scatter_3d` with real vs synthetic colour-coded; interactive rotation in HTML.
- **3D KDE surface** — optional; scipy `gaussian_kde` evaluated on a 3D grid, rendered as Plotly mesh/isosurface.

**Tasks:**
- [x] Implement `plot_feature_3d(real_df, synth_df, x, y, z)` → Plotly Figure
- [x] Implement `plot_feature_triple_grid(real_df, synth_df, triples)` → Plotly Figure (subplots)
- [x] Add 3D plots section to `generate_report()`
- [x] Tests: smoke-test that figures are returned without error

**Example triples to include by default:**
```python
DEFAULT_3D_TRIPLES = [
    ("rr_mean_ms", "hr_bpm", "qrs_duration_ms"),
    ("pr_interval_ms", "qt_interval_ms", "hrv_sdnn_ms"),
    ("st_deviation_mv", "t_amplitude_mv", "qrs_duration_ms"),
]
```

---

## 4. Integration & Report Updates

- [x] Integrate feature extraction + 2D/3D plots into the end-to-end `ecgen-eval eval` pipeline
- [x] Update `generate_report()` to accept optional `feature_df_real` and `feature_df_synth` arguments
- [x] Add a "Clinical Feature Summary" table to the HTML report (mean ± std, real vs synthetic, per feature)
- [x] Update `README.md` with feature extraction usage examples
- [x] Update `CLAUDE.md` architecture section once the `features/` subpackage is merged

---



---

## Implementation Order (Recommended)

1. **Feature extractor** (Task 1.2) — foundation for Tasks 2 & 3
2. **2D distribution plots** (Task 2) — immediate visual value
3. **3D distribution plots** (Task 3) — builds on 2D infrastructure
4. **Report integration** (Task 4) — ties everything together

