# ECG Feature Review — Top 10 Clinical Features for Synthetic ECG Evaluation

**Purpose:** Justify and document the clinical ECG features implemented in `ecgen_eval/features/` for evaluating the quality of synthetically generated ECG signals.

For a plain-language, interactive introduction, see [Clinical Features Explained](clinical/index.md).

---

## Selected Features

| # | Feature | Units | Clinical Relevance | Implemented |
|---|---------|-------|--------------------|-------------|
| 1 | **RR interval** (mean, std) | ms | Heart rate, rhythm regularity, arrhythmia detection | ✓ `rr_mean_ms`, `rr_std_ms` |
| 2 | **Heart Rate (HR)** | bpm | Bradycardia / tachycardia | ✓ `hr_bpm` |
| 3 | **PR interval** | ms | AV conduction; prolonged → 1st-degree AV block | ✓ `pr_interval_ms` |
| 4 | **QRS duration** | ms | Bundle branch blocks, ventricular conduction delay | ✓ `qrs_duration_ms` |
| 5 | **QT interval** | ms | Ventricular repolarisation; prolonged → long-QT syndrome | ✓ `qt_interval_ms` |
| 6 | **QTc (Bazett)** | ms | Rate-corrected QT: QT / √RR(s); arrhythmia risk marker | ✓ `qtc_bazett_ms` |
| 7 | **ST deviation** | mV | Displacement from isoelectric baseline; ischaemia / MI marker | ✓ `st_deviation_mv` |
| 8 | **T-wave amplitude** | mV | Hyperkalemia, ischaemia, LVH; affected by repolarisation | ✓ `t_amplitude_mv` |
| 9 | **P-wave duration** | ms | Atrial enlargement, inter-atrial conduction delay, AF risk | ✓ `p_wave_duration_ms` |
| 10 | **HRV — SDNN / RMSSD / pNN50** | ms / % | Autonomic tone; cardiac risk stratification; vagal activity | ✓ `hrv_sdnn_ms`, `hrv_rmssd_ms`, `hrv_pnn50` |

---

## Feature Descriptions and Clinical Context

### 1 & 2 — RR Interval and Heart Rate

The RR interval is the time between consecutive R-peaks measured in milliseconds. It directly encodes heart rate (HR = 60,000 / RR\_mean\_ms in bpm). Variation in RR interval (captured by `rr_std_ms`) reflects rhythm regularity. In a generative model evaluation context, the distribution of RR intervals and HR should match between real and synthetic ECG: divergence indicates the model has not learned the cardiac rhythm distribution.

**References:**
- AHA/ACC Electrocardiography Guidelines (2016)
- PhysioNet — RR interval definitions: https://physionet.org

### 3 — PR Interval

The PR interval spans from the onset of the P-wave to the onset of the QRS complex, reflecting the time for atrial depolarisation and AV nodal conduction. Normal range: 120–200 ms. Prolongation indicates first-degree AV block; shortening may indicate Wolff-Parkinson-White or junctional rhythms.

### 4 — QRS Duration

QRS duration spans the full ventricular depolarisation complex. Normal: 70–110 ms. Prolongation (>120 ms) indicates bundle branch block (LBBB, RBBB) or ventricular conduction abnormality. Synthetic ECGs should replicate the QRS width distribution of the training population.

### 5 & 6 — QT Interval and QTc

The QT interval spans from QRS onset to T-wave end, reflecting total ventricular repolarisation time. It is rate-dependent; QTc (Bazett's formula: QTc = QT / √RR\_s) adjusts for heart rate. Normal QTc: <440 ms (men), <460 ms (women). Prolonged QTc is a marker of risk for torsades de pointes.

**Reference:** Bazett HC (1920). *Heart* 7:353–370.

### 7 — ST Deviation

The ST segment (from QRS offset / J-point to T-wave onset) should be at the isoelectric baseline. Elevation (>1 mm) suggests acute myocardial infarction; depression suggests ischaemia or digoxin effect. In synthetic ECG evaluation, the ST deviation distribution should not be pathologically shifted unless the generative model is trained on a population with such pathology.

### 8 — T-wave Amplitude

The T-wave reflects ventricular repolarisation. Its amplitude is lead-dependent and varies with pathology: peaked T-waves in hyperkalemia or early STEMI; inverted T-waves in ischaemia and LVH. A generative model should reproduce the lead-specific T-wave amplitude distribution.

### 9 — P-wave Duration

P-wave duration (normal: 80–120 ms) reflects atrial depolarisation time. Prolongation indicates inter-atrial conduction delay (P-mitrale) and is a risk factor for atrial fibrillation. Absence of P-waves in synthetic output would indicate a fundamental failure to model sinus rhythm.

### 10 — HRV Metrics (SDNN, RMSSD, pNN50)

Time-domain HRV measures quantify the variation of RR intervals:
- **SDNN**: Standard deviation of all normal RR intervals — reflects overall HRV, both sympathetic and parasympathetic.
- **RMSSD**: Root mean square of successive RR differences — dominated by parasympathetic (vagal) modulation; robust to non-stationarity.
- **pNN50**: Percentage of successive RR differences >50 ms — correlated with RMSSD; indicator of vagal tone.

Low HRV (reduced SDNN/RMSSD) is associated with increased cardiac risk. Generative models that produce overly regular synthetic ECGs (low HRV) would fail these checks.

**References:**
- Task Force of ESC/NASPE (1996). Heart rate variability. *Circulation* 93:1043–1065.
- Makowski et al. (2021). NeuroKit2: A Python toolbox for neurophysiological signal processing. *Behavior Research Methods*.

---

## Algorithm Implementation Choices

| Task | Primary (neurokit2) | Fallback (scipy / NumPy) |
|------|--------------------|-----------------------------|
| R-peak detection | `nk.ecg_peaks()` (Pan-Tompkins) | Scipy bandpass + `find_peaks` |
| Full delineation (P, QRS, T) | `nk.ecg_delineate(method="peak")` | Heuristic windows around R-peaks |
| HRV computation | Manual from RR series | Manual from RR series (same) |

The heuristic fallback windows are based on typical ECG timing for a 60-bpm sinus rhythm and are adequate for **distribution-level** comparisons across large cohorts of real vs synthetic ECG. For individual beat-level clinical diagnostics, the neurokit2 path is strongly recommended.

---

## References

1. Goldberger AL et al. (2000). PhysioBank, PhysioToolkit, PhysioNet. *Circulation* 101:e215–e220.
2. Makowski D et al. (2021). NeuroKit2. *Behavior Research Methods* 53:1689–1696.
3. Task Force (ESC/NASPE) (1996). Heart rate variability: standards of measurement. *Circulation* 93:1043–1065.
4. Bazett HC (1920). An analysis of the time relations of electrocardiograms. *Heart* 7:353–370.
5. AHA/ACC/HRS (2016). Recommendations for the standardization and interpretation of the ECG. *J Am Coll Cardiol* 67:2516–2524.
6. Pan J, Tompkins WJ (1985). A real-time QRS detection algorithm. *IEEE Trans Biomed Eng* 32:230–236.
