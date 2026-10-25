# Clinical Features

Signal-level metrics tell you whether synthetic ECGs *look* statistically similar. Clinical
features tell you whether they are *physiologically plausible*: are the PR, QRS and QT
intervals in the right range, is the heart rate distribution right, is there realistic HRV?

The `ecgen_eval.features` subpackage extracts these features per recording so that
real and synthetic distributions can be compared numerically and visually.

## Installation

```bash
pip install "ecgen-eval[features]"    # neurokit2 + scipy
```

Without NeuroKit2 the extractor still runs, using a SciPy-based Pan–Tompkins R-peak detector
and heuristic windows around R-peaks for delineation. Results are less accurate.

## Extracted features

| Feature | Column(s) in `summary_df` | Unit |
|---|---|---|
| RR interval | `rr_mean_ms`, `rr_std_ms` | ms |
| Heart rate | `hr_bpm` | bpm |
| PR interval | `pr_interval_ms` | ms |
| QRS duration | `qrs_duration_ms` | ms |
| QT interval | `qt_interval_ms` | ms |
| QTc (Bazett, QT/√RR) | `qtc_bazett_ms` | ms |
| P-wave duration | `p_wave_duration_ms` | ms |
| ST deviation | `st_deviation_mv` | mV (signal units) |
| T-wave amplitude | `t_amplitude_mv` | mV (signal units) |
| HRV | `hrv_sdnn_ms`, `hrv_rmssd_ms`, `hrv_pnn50` | ms, ms, % |

`summary_df` also has a `sample_idx` column. Features that cannot be measured for a recording
(e.g. too few beats) are `NaN`.

The clinical rationale for each feature is discussed in the
[ECG Feature Review](../ecg_features_review.md).

## How extraction works

[![Feature extraction: R-peaks and delineation on the primary lead, amplitudes on every lead, aggregated into summary_df and beat_df](../assets/diagrams/features-light.svg#only-light){ .ecgen-diagram }](../assets/diagrams/features-light.svg "Open full size")
[![Feature extraction: R-peaks and delineation on the primary lead, amplitudes on every lead, aggregated into summary_df and beat_df](../assets/diagrams/features-dark.svg#only-dark){ .ecgen-diagram }](../assets/diagrams/features-dark.svg "Open full size")

For each recording:

1. **R-peaks** are detected on a single *primary lead* — `lead_for_intervals`, default
   `"II"`, falling back to the first lead if absent — with `nk.ecg_peaks()`.
2. **Delineation** (P, QRS, T onsets/peaks/offsets) on the primary lead with
   `nk.ecg_delineate()`.
3. **RR/HR, intervals and HRV** are derived from the primary lead.
4. **ST deviation and T-wave amplitude** are measured on **every lead** and averaged into the
   summary row.

!!! note "Amplitude units"
    ST and T amplitudes are reported in the units of your input signal. Column names say
    `mv` because ECGs are conventionally stored in millivolts — make sure yours are.

## Python API

```python
from ecgen_eval import load_ecg_npy
from ecgen_eval.features import extract_features, FeatureExtractor

real = load_ecg_npy("real.npy", fs=500, label="PTB-XL")
synth = load_ecg_npy("synth.npy", fs=500, label="ECGEN-FM")

beat_real, summ_real = extract_features(real)
beat_synth, summ_synth = extract_features(synth)

# Use a different lead for timing
extractor = FeatureExtractor(lead_for_intervals="V5")
beat_df, summary_df = extractor.extract(real)
```

### Output tables

`summary_df` — one row per recording, the columns listed above.

`beat_df` — one row per *(recording, beat, lead)*:

| Column | Meaning |
|---|---|
| `sample_idx` | Recording index |
| `beat_idx` | Beat index within the recording |
| `lead` | Lead name |
| `r_sample` | R-peak position (sample index) |
| `rr_ms` | RR interval following the beat |
| `st_deviation_mv`, `t_amplitude_mv` | Lead-level amplitude features |

### Comparing distributions

```python
cols = ["hr_bpm", "pr_interval_ms", "qrs_duration_ms", "qtc_bazett_ms", "hrv_sdnn_ms"]

comparison = (
    summ_real[cols].describe().T[["mean", "std"]]
    .join(summ_synth[cols].describe().T[["mean", "std"]], lsuffix="_real", rsuffix="_synth")
)
print(comparison.round(1))
```

A two-sample test per feature is a quick way to flag the biggest mismatches:

```python
from scipy.stats import ks_2samp

for c in cols:
    stat, p = ks_2samp(summ_real[c].dropna(), summ_synth[c].dropna())
    print(f"{c:>18}  KS={stat:.3f}  p={p:.3g}")
```

## Plots

2D and 3D distribution plots are described in [Visualization](visualization.md#clinical-feature-plots).
In reports, enable them with `--feature-plots` (CLI) or the `feature_*` arguments of
[`generate_report`](reports.md).

## CLI

Export a combined CSV with a `dataset` column identifying each source:

```bash
ecgen-eval features \
  --real real.npy \
  --synthetic model_a.npy --synthetic model_b.npy \
  --lead II --fs 500 \
  --output features.csv
```
