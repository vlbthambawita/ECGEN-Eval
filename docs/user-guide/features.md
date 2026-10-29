# Clinical Features

Signal-level metrics tell you whether synthetic ECGs *look* statistically similar. Clinical
features tell you whether they are *physiologically plausible*: are the PR, QRS and QT
intervals in the right range, is the heart rate distribution right, is there realistic HRV?

The `ecgen_eval.features` subpackage extracts these features per recording so that
real and synthetic distributions can be compared numerically and visually.

!!! tip "New to ECGs?"
    [Clinical Features Explained](../clinical/index.md) explains every feature in plain language,
    with interactive heartbeats. It also shows how the extractor
    [compares with commercial ECG software](../clinical/index.md#validation).

## Installation

```bash
pip install "ecgen-eval[features]"    # neurokit2 + scipy
```

Without NeuroKit2 the extractor still runs: R peaks come from a SciPy-based Pan–Tompkins
detector, and heart rate, HRV, QRS duration, ST deviation and T amplitude are still measured.
PR, QT, QTc and P-wave duration need NeuroKit2's P/T delineation and are `NaN` without it.

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

Extraction has two stages: a **delineation backend** finds the beats and their fiducial points,
then the selected **feature groups** measure them (see
[Choosing features and libraries](#choosing-features-and-libraries)). The steps below describe
the default `hybrid` backend.

[![Feature extraction: a selectable delineation backend finds R peaks and fiducials, then the selected feature groups fill summary_df and beat_df](../assets/diagrams/features-light.svg#only-light){ .ecgen-diagram }](../assets/diagrams/features-light.svg "Open full size")
[![Feature extraction: a selectable delineation backend finds R peaks and fiducials, then the selected feature groups fill summary_df and beat_df](../assets/diagrams/features-dark.svg#only-dark){ .ecgen-diagram }](../assets/diagrams/features-dark.svg "Open full size")

For each recording:

1. **R-peaks** are detected on a single *primary lead* — `lead_for_intervals`, default
   `"II"`, falling back to the first lead if absent — with `nk.ecg_clean()` +
   `nk.ecg_peaks()`. They define the beats; RR, HR and HRV come from them.
2. **Delineation uses every lead** (`ecgen_eval.features.delineation`):
    - **QRS onset and offset** from the *spatial velocity* (sum of absolute slopes over all
      leads): the QRS is where it stays above 4 % of its range around each R peak. This
      needs only NumPy/SciPy.
    - **P onset/offset and T peak** from NeuroKit2's peak-prominence delineator
      (`nk.ecg_delineate(method="prominence")`) on every lead with that lead's own R peaks.
      P boundaries are refined to 15 % of the P amplitude.
    - **T offset** with the tangent method: the steepest return of the T wave to the
      baseline, extended as a line to the baseline level.
    - Per-lead points are assigned to the reference beats and combined with the median
      across leads.
3. **Intervals** are computed per beat (PR = QRS onset − P onset, QRS = offset − onset,
   QT = T offset − QRS onset, P = P offset − P onset), beats outside plausible ranges
   are dropped, and the summary is the **median over beats**. QTc = QT / √(mean RR in s).
4. **ST deviation and T-wave amplitude** are measured on **every lead** against the PR-segment
   baseline (QRS onset − 40 to − 10 ms): ST at J + 80 ms, T as the signed extreme between
   J + 80 ms and the T offset. Each lead takes the median over beats; the summary averages
   the leads.

Accuracy against the GE 12SL measurements of PTB-XL+ is summarised in
[Clinical Features Explained → Validation](../clinical/index.md#validation). Interval
accuracy is best with several leads at ≥ 250 Hz; with a single lead the QRS duration is
noticeably less accurate.

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
| `pr_interval_ms`, `qrs_duration_ms`, `qt_interval_ms`, `p_wave_duration_ms` | Intervals of this beat (same for every lead; `NaN` if not measurable) |
| `st_deviation_mv`, `t_amplitude_mv` | Lead-level amplitude features (median over beats) |

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

## Choosing features and libraries

The extractor has two independent choices: **which features** to compute and **which
library** finds the beats and their P/QRS/T boundaries. Every feature works with every
library.

### Selecting features

Features are organised in groups. Pass group names, single columns, or both with `features=`
(CLI: `-F/--feature`, repeatable). Run `ecgen-eval list-features` to see what is registered.

| Group | Columns |
|---|---|
| `rhythm` | `rr_mean_ms`, `rr_std_ms`, `hr_bpm` |
| `intervals` | `pr_interval_ms`, `qrs_duration_ms`, `qt_interval_ms`, `qtc_bazett_ms`, `p_wave_duration_ms` |
| `hrv` | `hrv_sdnn_ms`, `hrv_rmssd_ms`, `hrv_pnn50` |
| `amplitude` | `st_deviation_mv`, `t_amplitude_mv` |

```python
from ecgen_eval.features import FeatureExtractor

# HRV group plus two single columns
fe = FeatureExtractor(features=["hrv", "hr_bpm", "qtc_bazett_ms"])
beat_df, summary_df = fe.extract(real)
fe.columns   # ['hrv_sdnn_ms', 'hrv_rmssd_ms', 'hrv_pnn50', 'hr_bpm', 'qtc_bazett_ms']
```

`beat_df` only carries the per-beat / per-lead columns of the selected features. Without
`features=` (or with `"all"`) every registered group is computed.

### Choosing the extraction library (backend)

| Backend | R peaks | QRS boundaries | P / T waves | Needs |
|---|---|---|---|---|
| `hybrid` *(default)* | NeuroKit2 `ecg_peaks` | Spatial velocity of all leads | NeuroKit2 `prominence` on every lead, tangent T offset | `neurokit2`, `scipy` |
| `neurokit2` | NeuroKit2 `ecg_peaks` | NeuroKit2 `ecg_delineate` | NeuroKit2 `ecg_delineate` (`dwt`, `cwt`, `peak`, `prominence`) | `neurokit2` |
| `scipy` | SciPy Pan–Tompkins | Spatial velocity of all leads | — (PR, QT, QTc, P duration are `NaN`) | `scipy` |

```python
# Plain NeuroKit2 with the DWT delineator, every lead combined with the median
fe = FeatureExtractor(backend="neurokit2", delineation_method="dwt",
                      backend_kwargs={"leads": "all"})

# Default backend with a different R-peak detector
fe = FeatureExtractor(rpeak_method="pantompkins1985")

# No NeuroKit2 at all
fe = FeatureExtractor(backend="scipy", features=["rhythm", "hrv", "qrs_duration_ms"])
```

`rpeak_method` accepts any [`nk.ecg_peaks`](https://neuropsychology.github.io/NeuroKit/functions/ecg.html#ecg-peaks)
method, or `"scipy"`. The `neurokit2` backend delineates the primary lead by default
(`leads="all"` delineates every lead at the primary lead's R peaks). Its `peak` method gives no
QRS boundaries, so QRS duration, PR, QT and the amplitudes are `NaN`.

!!! warning "Compare like with like"
    Different backends give systematically different intervals (e.g. QT from `dwt` is
    typically longer than from `hybrid`). Always extract real and synthetic data with the
    **same** extractor. Only `hybrid` has been
    [validated against GE 12SL](../clinical/index.md#validation).

### Adding your own features

A feature is a function of a `RecordingContext` — the recording `(L, T)`, `lead_names`, `fs`,
`primary_lead_idx`, the R peaks (`rpeaks`) and the fiducials found by the backend (`waves`,
arrays aligned with `rpeaks` under keys such as `ECG_QRS_Onsets`, `ECG_T_Offsets`). Pass it
directly, or register it so it can be selected by name (also from `list-features`):

```python
import numpy as np
from ecgen_eval.features import FeatureExtractor, feature_group

def n_beats(ctx):
    return {"n_beats": ctx.n_beats}

@feature_group("qrs_area", columns=["qrs_area_mv_ms"])
def qrs_area(ctx):
    """Median absolute QRS area on the primary lead."""
    on, off = ctx.waves["ECG_QRS_Onsets"], ctx.waves["ECG_QRS_Offsets"]
    sig = ctx.primary_signal
    areas = [np.abs(sig[int(a):int(b)]).sum() / ctx.fs * 1000
             for a, b in zip(on, off) if np.isfinite(a) and np.isfinite(b)]
    return {"qrs_area_mv_ms": float(np.median(areas)) if areas else np.nan}

fe = FeatureExtractor(features=["intervals", "qrs_area", n_beats])
```

For per-beat or per-lead values in `beat_df`, subclass `FeatureGroup` and implement
`compute`, `per_beat` and/or `per_lead`, then call `register_feature_group(MyGroup())`.
A feature that raises for a recording gives `NaN` for that recording, with one warning.

### Adding your own library

Subclass `DelineationBackend` and return the R peaks and the fiducial arrays; any library
(e.g. your own deep-learning delineator) then works with every feature group:

```python
import numpy as np
from ecgen_eval.features import DelineationBackend, FeatureExtractor, register_backend

@register_backend
class MyDelineator(DelineationBackend):
    name = "mylib"
    description = "My delineation model"

    def delineate(self, recording, fs, primary_lead_idx):
        rpeaks = ...                       # (M,) sample indices
        waves = {
            "ECG_QRS_Onsets": ...,         # each (M,), NaN where missing
            "ECG_QRS_Offsets": ...,
            "ECG_P_Onsets": ..., "ECG_P_Offsets": ...,
            "ECG_T_Peaks": ..., "ECG_T_Offsets": ...,
        }
        return rpeaks, waves

fe = FeatureExtractor(backend="mylib")        # or backend=MyDelineator()
```

Missing keys simply make the features that need them `NaN`.

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
