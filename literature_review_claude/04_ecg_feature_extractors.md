# Open-Access ECG Feature Extractors Usable from Python

**Date:** 2026-10-28 · **Purpose:** find open-source tools that extract ECG features and can be
used from Python. The main goal is to choose a replacement or cross-check for ECGEN-Eval's
clinical feature extractor (`ecgen_eval/features/`), whose interval features are currently
unreliable (see `docs/clinical/index.md#known-limitations`).

## Method

- **Sources:** web and literature search (software papers in JOSS, SoftwareX, JORS, CinC,
  Frontiers and IEEE Access; delineation benchmarks; PyPI; GitHub).
- **Search terms:** combinations of *ECG feature extraction / delineation / fiducial points /
  intervals / HRV / signal quality / R-peak detection* with *Python, toolbox, package, open
  source*.
- **Verification (2026-10-28):** every entry was checked directly.
  - **PyPI JSON API:** latest version, release date, licence, supported Python.
  - **GitHub API:** licence, stars, last push, language, README.
  - **Crossref:** every paper DOI listed below resolves to the stated title.
- **Inclusion:** (1) the source code is public; (2) it runs from Python, either natively or
  through a documented runtime; (3) it outputs ECG-derived features. These cover fiducial
  points, intervals, amplitudes, heart rate, HRV and signal quality. Generic time-series
  feature libraries are listed separately.
- **Exclusion:** file readers only (e.g. `pyECG`, which only does dataset I/O); MATLAB-only
  tools (listed in [§9](#9-non-python-reference-tools) for context); closed engines.

Status legend: ✅ maintained (release or push in the last ~12 months) · ⚠️ stale
(> 2 years without a release) · 🔒 licence restriction worth noting.

---

## 1. Quick answer

| Need | Best open Python options | Notes |
|---|---|---|
| **P/QRS/T delineation → PR, QRS, QT, P duration, ST, T** | **NeuroKit2** (`ecg_delineate`, methods `dwt` / `prominence`), **prominence-delineator**, **PQRSTann**, **pecg** (PhysioZoo) | Independent benchmarks rank prominence-based delineation above NeuroKit2's wavelet methods; `pecg` needs the MATLAB Runtime |
| **R peaks / heart rate** | `wfdb.processing` (XQRS/GQRS), NeuroKit2, BioSPPy, py-ecg-detectors, SleepECG | Many validated detectors; ECGEN-Eval's own detector reaches 91 % within 5 bpm on PTB-XL |
| **HRV (time / frequency / nonlinear)** | hrv-analysis, pyHRV, NeuroKit2, HeartPy, Systole, SleepECG | Choose by licence; all work from RR series |
| **Signal quality** | vital_sqi (74 SQIs), NeuroKit2 `ecg_quality`, BioSPPy (`bSQI`, `kSQI`, `pSQI`, `fSQI`, `ZZ2018`), ecg_qc | |
| **ML feature tables** | FeatureDB (PKU), ECG-featurizer, pyheartlib | FeatureDB has no licence file |
| **Learned delineation (train your own)** | torch_ecg, ckjoung/ecg-segmentation, DelineatorSwitchAndCompose, HeartKit | Only HeartKit publishes pretrained segmentation weights (single lead, 100 Hz, 2.56 s frames, TensorFlow); none ships 12-lead delineation weights |
| **Generic time-series features** | TSFEL, tsfresh, pycatch22, AntroPy, nolds, EntropyHub | Not clinically interpretable, but useful extra descriptors |

---

## 2. Delineation and clinical interval / morphology features

These tools find P, QRS and T onsets, peaks and offsets, from which the clinical features follow.

| Tool | What it extracts | Method | Install | Licence | Version (date) | Status | Paper |
|---|---|---|---|---|---|---|---|
| **[NeuroKit2](https://github.com/neuropsychology/NeuroKit)** | R peaks; P, Q, S, T peaks; P/R/T onsets and offsets (`dwt`); ECG quality; HRV. No interval columns: `ecg_intervalrelated` returns only mean rate + HRV, so PR/QRS/QT must be computed from the fiducials | `ecg_delineate(method=` `peak` · `cwt` · `dwt` · `prominence` `)` | `pip install neurokit2` | MIT | 0.2.13 (2026-03-02) | ✅ 2.4k★ | Makowski et al., *Behav Res Methods* 2021, [10.3758/s13428-020-01516-y](https://doi.org/10.3758/s13428-020-01516-y) |
| **[prominence-delineator](https://github.com/JonasEmrich/prominence-delineator)** | P, R, T positions, onsets and offsets; single or multi-lead (`find_waves_multilead`); ECG cleaning and R-peak detection (FastNVG) | Physiology-informed peak-prominence wave selection | `pip install prominence-delineator` | GPL-3.0 🔒 | 0.0.x (repo pushed 2026-01) | ✅ | Emrich et al., *EUSIPCO* 2024, [10.23919/EUSIPCO63174.2024.10715353](https://doi.org/10.23919/EUSIPCO63174.2024.10715353) |
| **[PQRSTann](https://github.com/foreverallama/PQRSTann)** | Beat-by-beat P, QRS and T peaks and boundaries; WFDB/CSV annotation output; adult and fetal settings | Python re-implementation of PhysioNet **ECGPUWAVE** (Pan–Tompkins + boundary rules) | `pip install pqrstann` | BSD-3 (repo) / MIT (PyPI metadata) | 0.1.0 (2026-03-27) | ✅ new, 0★; Zenodo [10.5281/zenodo.19217332](https://doi.org/10.5281/zenodo.19217332) | — |
| **[pecg / PhysioZoo ECG](https://github.com/aim-lab/PECG)** (formerly `pebm`) | 22 biomarkers per channel: 14 interval/segment durations (PR, QRS, QT, QTc, P, T, …) and 8 wave characteristics; 6 summary statistics each | epltd R peaks + **wavedet** fiducials | `pip install pecg` (+ `wfdb`) | MIT | 2.0.5 (2023-05-16) | ⚠️ wavedet needs the **MATLAB Runtime 2021a** | Gendelman et al., *CinC* 2021, [10.23919/CinC53138.2021.9662857](https://doi.org/10.23919/CinC53138.2021.9662857) |
| **[BioSPPy](https://github.com/scientisst/BioSPPy)** | R peaks (Hamilton, Christov, Engelse–Zeelenberg, Gamboa, SSF, ASI, Pan–Tompkins++); `getPPositions`, `getQPositions`, `getSPositions`, `getTPositions`; heartbeat templates; SQIs | Detectors + rule-based wave positions | `pip install biosppy` | BSD-3 | 2.2.4 (2025-11-07) | ✅ | Bota et al., *SoftwareX* 2024, [10.1016/j.softx.2024.101712](https://doi.org/10.1016/j.softx.2024.101712) |
| **[FeatureDB](https://github.com/PKUDigitalHealth/FeatureDB)** (PKU Digital Health) | Average beat, PR, QRS, QT, QTc, **QRS axis**, **QT dispersion**, frequency-domain, HRV and morphologic-variability features | Adaptive peak detection + wavelet refinement | clone the repo (no PyPI) | **none stated** 🔒 | — (pushed 2025-08-04) | ✅ 30★ | Hong et al., *Physiol Meas* 2019, [10.1088/1361-6579/ab15a2](https://doi.org/10.1088/1361-6579/ab15a2); wearable validation arXiv [2502.17499](https://arxiv.org/abs/2502.17499) |
| **[pyECGdeli](https://github.com/axel-loewe/pyECGdeli)** | QRS detection only so far (port of MATLAB ECGdeli) | Wavelet / ECGdeli | clone the repo | GPL-3.0 | — (pushed 2022-08-29) | ⚠️ work in progress, P/T not ported | — |
| **[ecg_processing](https://github.com/dieterich-lab/ecg_processing)** (Dieterich lab) | 12-lead pipeline: R peaks, P/QRS/T delineation, HR, PR, QT, … | Wraps NeuroKit2 | clone + `requirements.txt` | **none stated** 🔒 | — (pushed 2025-06-25) | ✅ small | — |
| **ecg-records / ecgfeat** | 12-lead record-level P, PR, QRS, QT, QTc, axes; per-beat fiducials | Compiled engine | `pip install ecg-records` | Apache-2.0 wrapper; **engine PolyForm Noncommercial, compiled wheels** 🔒 | 0.3.2 (2026-10-19) | not open source (engine) | — |

**Benchmarks of these delineators:**

- Jaeger et al. (2024), *IEEE Access* 12, 160794–160804,
  [10.1109/ACCESS.2024.3487013](https://doi.org/10.1109/ACCESS.2024.3487013).
  Compares NeuroKit, ECG-kit and ECGdeli on LUDB, QTDB and two smartwatch datasets. ECGdeli
  was the most stable. NeuroKit had lower sensitivity but good timing accuracy for the points
  it did find.
- Emrich et al. (2024), EUSIPCO
  ([10.23919/EUSIPCO63174.2024.10715353](https://doi.org/10.23919/EUSIPCO63174.2024.10715353)).
  Introduces the prominence delineator, since also available in NeuroKit2 as
  `method="prominence"`.
- Lim et al. (2026), *Label-Efficient Deep Learning for ECG Delineation*, arXiv
  [2610.07885](https://arxiv.org/abs/2610.07885).
  - Among the existing tools, ECGdeli and Prominence rank top.
  - On LUDB, NeuroKit2 scores 59.9 (CWT) and 62.2 (DWT) against 80.6 for ECGdeli.
  - The paper's deep model beats all tools. No code or weights are released.
- PTB-XL+ (PhysioNet) provides **ECGdeli**, GE **12SL** and Philips **Uni-G** features for all
  21,799 PTB-XL records. It is the reference we used to validate ECGEN-Eval's extractor.

---

## 3. Deep-learning delineation (code to train or fine-tune)

| Tool | What it does | Licence | Weights in repo? | Paper |
|---|---|---|---|---|
| **[torch_ecg](https://github.com/DeepPSP/torch_ecg)** (`pip install torch-ecg`, 0.0.33, 2026-10-12) | PyTorch ECG framework: preprocessing, augmentation, CRNN, U-Net and sequence tagging for wave segmentation, dataset readers (incl. LUDB) | MIT | check the docs | Wen & Kang, *Physiol Meas* 2022, [10.1088/1361-6579/ac9451](https://doi.org/10.1088/1361-6579/ac9451) |
| **[ecg-segmentation](https://github.com/ckjoung/ecg-segmentation)** (Joung et al.) | 1-D U-Net, UNet 3+ and UNet 3+ with arrhythmia branch; per-sample P / QRS / T / none labels; LUDB training scripts | MIT | **no** (training code only) | Joung et al., *PLOS ONE* 2024, [10.1371/journal.pone.0303178](https://doi.org/10.1371/journal.pone.0303178) |
| **[DelineatorSwitchAndCompose](https://github.com/guillermo-jimenez/DelineatorSwitchAndCompose)** | CNN detection and delineation trained on synthetically augmented beats | GPL-3.0 | check repo | Jiménez-Pérez et al., *Front Cardiovasc Med* 2024, [10.3389/fcvm.2024.1341786](https://doi.org/10.3389/fcvm.2024.1341786) |
| **[HeartKit](https://github.com/AmbiqAI/heartkit)** (`pip install heartkit`, 1.8.0, 2026-01-16) + **[PhysioKit](https://github.com/AmbiqAI/physiokit)** (0.11.0) | Single-lead tasks: denoising, P/QRS/T **segmentation**, rhythm and beat classification; PhysioKit adds cleaning, peaks, HRV and synthesis | BSD-3 | **yes**: seg-4-tcn-sm/lg, seg-2-tcn-sm in the Ambiq model zoo (single lead, 100 Hz, 256-sample frames, per-sample NONE/P/QRS/T) | — |

---

## 4. R-peak detection and heart rate

| Tool | Detectors / outputs | Licence | Version (date) | Paper |
|---|---|---|---|---|
| **[wfdb-python](https://github.com/MIT-LCP/wfdb-python)** (`wfdb.processing`) | XQRS, GQRS, `compute_hr`, `correct_peaks`; reads PhysioNet data | MIT | 4.3.1 (2026-02-03) ✅ | PhysioNet: Goldberger et al., *Circulation* 2000 |
| **[py-ecg-detectors](https://github.com/berndporr/py-ecg-detectors)** | 8 detectors: Hamilton, Christov, Engelse–Zeelenberg, Pan–Tompkins, SWT, two-average, matched filter, WQRS; plus an HRV module | GPL-3.0 🔒 | 1.3.5 (2024-01-22) | Zenodo [10.5281/zenodo.3353396](https://doi.org/10.5281/zenodo.3353396) |
| **[SleepECG](https://github.com/cbrnr/sleepecg)** | Fast heartbeat detector (C extension or Numba) and 26 time-domain + 7 frequency-domain HRV features | BSD-3 | 0.6.0 (2026-10-07) ✅ | Brunner & Hofer, *JOSS* 2023, [10.21105/joss.05411](https://doi.org/10.21105/joss.05411) |
| **NeuroKit2**, **BioSPPy** | many detectors (see §2) | MIT, BSD-3 | | |
| **[MNE-Python](https://github.com/mne-tools/mne-python)** | `mne.preprocessing.find_ecg_events` (QRS events in EEG/MEG recordings) | BSD-3 | 1.13.2 (2026-09-11) ✅ | Gramfort et al., *Front Neurosci* 2013, [10.3389/fnins.2013.00267](https://doi.org/10.3389/fnins.2013.00267) |
| **[Systole](https://github.com/LegrandNico/systole)** | ECG/PPG peak detection, artefact correction, HRV, cardiac-cycle synchrony | GPL-3.0 🔒 | 0.3.1 (2025-04-07) | Legrand & Allen, *JOSS* 2022, [10.21105/joss.03832](https://doi.org/10.21105/joss.03832) |

---

## 5. Heart-rate variability (HRV) feature libraries

All of these work from R peaks or an RR series, so they can be paired with any detector above.

| Tool | Feature domains | Licence | Version (date) | Paper |
|---|---|---|---|---|
| **[hrv-analysis](https://github.com/Aura-healthcare/hrv-analysis)** (`hrvanalysis`) | Outlier and ectopic removal; time, frequency (Welch, Lomb–Scargle), geometric, Poincaré, CSI/CVI | GPL-3.0 🔒 | 1.0.6 (2026-06-02) ✅ | Champseix et al., *JORS* 2021, [10.5334/jors.305](https://doi.org/10.5334/jors.305) |
| **[pyHRV](https://github.com/PGomes92/pyhrv)** | 78 parameters: 23 time, 48 frequency, 7 nonlinear (Poincaré, sample entropy, DFA); compared against Kubios | BSD-3 | 0.5.0 (2026-06-17) ✅ | Gomes et al., *IcETRAN* 2019 (no DOI) |
| **NeuroKit2** (`hrv_time`, `hrv_frequency`, `hrv_nonlinear`, `hrv_rqa`) | The broadest set, incl. many entropy and fractal indices | MIT | see §2 | Makowski et al. 2021 |
| **[HeartPy](https://github.com/paulvangentcom/heartrate_analysis_python)** | Noise-robust peaks for PPG and ECG; BPM, IBI, SDNN, RMSSD, pNN50, LF/HF, breathing rate | MIT (repo) / GPL (PyPI metadata) | 1.2.7 (2021-03-20) ⚠️ | van Gent et al., *JORS* 2019, [10.5334/jors.241](https://doi.org/10.5334/jors.241) |
| **[BioPsyKit](https://github.com/mad-lab-fau/biopsykit)** | ECG pipeline on NeuroKit2: R-peak outlier correction, HRV, ECG-derived respiration | MIT | 0.14.0 (2026-10-02) ✅ | Richer et al., *JOSS* 2021, [10.21105/joss.03702](https://doi.org/10.21105/joss.03702) |
| **[physio](https://github.com/samuelgarcia/physio)** (CRNL Lyon) | ECG peaks, HRV time/frequency, respiratory-HRV coupling | MIT | 0.3.3 (2026-03-19) ✅ | — |
| **[FLIRT](https://github.com/im-ethz/flirt)** | Wearable HRV feature windows (ECG/PPG IBIs), EDA, accelerometer | custom (NOASSERTION) 🔒 | 0.0.2 (2021-03-19) ⚠️ | Föll et al., *Comput Methods Programs Biomed* 2021, [10.1016/j.cmpb.2021.106461](https://doi.org/10.1016/j.cmpb.2021.106461) |
| **[biopeaks](https://github.com/JanCBrammer/biopeaks)** | GUI for ECG/PPG/respiration peak extraction and rate/variability features | GPL-3.0 🔒 | 1.4.4 (2022-01-05) ⚠️ | Brammer, *JOSS* 2020, [10.21105/joss.02621](https://doi.org/10.21105/joss.02621) |

---

## 6. Signal-quality indices (SQI)

| Tool | What it computes | Licence | Version (date) | Paper |
|---|---|---|---|---|
| **[vital_sqi](https://github.com/meta00/vital_sqi)** (`pip install vital-sqi`) | 74 SQIs for ECG and PPG, rule-based accept/reject, GUI | MIT | 0.1.0 (2022-08-11) ⚠️ (repo pushed 2024-11) | Le et al., *Front Physiol* 2022, [10.3389/fphys.2022.1020458](https://doi.org/10.3389/fphys.2022.1020458) |
| **NeuroKit2** `ecg_quality` | Template-correlation quality and the Zhao 2018 method | MIT | see §2 | |
| **BioSPPy** | `bSQI`, `sSQI`, `kSQI`, `pSQI`, `fSQI`, `ZZ2018` | BSD-3 | see §2 | |
| **[ecg_qc](https://github.com/Aura-healthcare/ecg_qc)** (`pip install ecg-qc`) | SQIs + pretrained noisy/clean classifier | GPL-3.0 🔒 | 1.0b6 (2021-09-22) ⚠️ | — |

---

## 7. ML-oriented ECG feature tables

| Tool | What it produces | Licence | Version (date) | Paper |
|---|---|---|---|---|
| **[FeatureDB](https://github.com/PKUDigitalHealth/FeatureDB)** | Expert features (see §2), used in the ENCASE PhysioNet 2017 entry | none stated 🔒 | repo only | Hong et al. 2017 (CinC) / 2019 (*Physiol Meas*) |
| **[ECG-featurizer](https://github.com/Bsingstad/ECG-featurizer)** | Tabular features from WFDB records via NeuroKit2: HR statistics, intervals, amplitudes, age, sex | GPL-3.0 🔒 | 1.0.7 (2021-05-04) ⚠️ | — |
| **[pyheartlib](https://github.com/devnums/pyheartlib)** | Beat and rhythm excerpts with computed features for ML (WFDB input) | AGPL-3.0 🔒 | 1.22.0 (2024-01-27) | Mohammadi, *JOSS* 2024, [10.21105/joss.05792](https://doi.org/10.21105/joss.05792) |
| **[ECGomics](https://github.com/PKUDigitalHealth/ECGomics)** | Web platform for structural, intensity, functional and comparative ECG biomarkers | none stated | web service; repo holds docs only | Zhang et al., arXiv [2601.15326](https://arxiv.org/abs/2601.15326) (2026) |

---

## 8. Generic time-series feature libraries (applicable to ECG)

These are not ECG-specific, but they are widely used as additional descriptors of ECG segments
or RR series.

| Tool | Features | Licence | Version (date) | Paper |
|---|---|---|---|---|
| **[TSFEL](https://github.com/fraunhoferportugal/tsfel)** | 60+ statistical, temporal, spectral and fractal features; ships an ECG example | BSD-3 | 0.2.0 (2025-08-20) ✅ | Barandas et al., *SoftwareX* 2020, [10.1016/j.softx.2020.100456](https://doi.org/10.1016/j.softx.2020.100456) |
| **[tsfresh](https://github.com/blue-yonder/tsfresh)** | Hundreds of features with hypothesis-test feature selection | MIT | 0.21.2 (2026-05-31) ✅ | Christ et al., *Neurocomputing* 2018, [10.1016/j.neucom.2018.03.067](https://doi.org/10.1016/j.neucom.2018.03.067) |
| **[pycatch22](https://github.com/DynamicsAndNeuralSystems/pycatch22)** | 22 canonical time-series characteristics (fast, C core) | GPL-3.0 🔒 | 1.0.2 (2026-10-20) ✅ | Lubba et al., *Data Min Knowl Disc* 2019, [10.1007/s10618-019-00647-x](https://doi.org/10.1007/s10618-019-00647-x) |
| **[AntroPy](https://github.com/raphaelvallat/antropy)** | Entropy (sample, approximate, spectral, SVD, permutation) and fractal dimensions | BSD-3 | 0.2.3 (2026-10-17) ✅ | — |
| **[nolds](https://github.com/CSchoel/nolds)** | Nonlinear measures: DFA, Hurst, Lyapunov, correlation dimension, sample entropy | MIT | 0.6.3 (2025-11-30) ✅ | — |
| **[EntropyHub](https://github.com/MattWillFlood/EntropyHub)** | 40+ entropy measures (incl. multiscale, cross and bidimensional) | Apache-2.0 | 2.0 (2024-04-24) | Flood & Grimm, *PLOS ONE* 2021, [10.1371/journal.pone.0259448](https://doi.org/10.1371/journal.pone.0259448) |

---

## 9. Non-Python reference tools

These are often used as the reference in benchmarks, but they have no maintained Python
interface.

| Tool | Language | Licence | Note |
|---|---|---|---|
| [ECGdeli](https://github.com/KIT-IBT/ECGdeli) | MATLAB | GPL-3.0 | Top-ranked open delineator in independent benchmarks; Pilia et al., *SoftwareX* 2021, [10.1016/j.softx.2020.100639](https://doi.org/10.1016/j.softx.2020.100639). Partial Python port: pyECGdeli (§2). |
| [ECG-kit](https://github.com/marianux/ecg-kit) | MATLAB | GPL-2.0 | Includes wavedet; last push 2020 |
| [PhysioNet Cardiovascular Signal Toolbox](https://github.com/cliffordlab/PhysioNet-Cardiovascular-Signal-Toolbox) | MATLAB | BSD-3 | HRV and SQI reference implementation; last push 2023 |
| [ECGPUWAVE](https://physionet.org/content/ecgpuwave/1.3.4/) | Fortran / C (WFDB) | GPL | Command-line delineator; re-implemented in Python by PQRSTann |
| GE 12SL, Philips Uni-G | commercial | proprietary | Not available as code, but their measurements for every PTB-XL record are published in **PTB-XL+** |

---

## 10. Implications for ECGEN-Eval

1. **Fix the extractor with what is already a dependency.** ECGEN-Eval already uses NeuroKit2,
   and the installed version (0.2.12) supports `ecg_delineate(method="dwt")`, which returns P,
   R and T onsets and offsets, and `method="prominence"`. The extractor currently calls
   `method="peak"` and reads keys that this method never returns. Switching method and key
   names is the smallest change. It should be validated against PTB-XL+ 12SL, as was done for
   heart rate.
2. **Use a second delineator as a cross-check.** The prominence method is also available
   standalone (`prominence-delineator`, GPL-3.0). PQRSTann provides an independent
   ECGPUWAVE-style result. Comparing two delineators on real data gives a sense of measurement
   uncertainty.
3. **Licences.** ECGEN-Eval is Apache-2.0. MIT and BSD dependencies (NeuroKit2, BioSPPy,
   pyHRV, SleepECG, wfdb, TSFEL, tsfresh, AntroPy) are compatible. GPL/AGPL packages
   (prominence-delineator, hrv-analysis, py-ecg-detectors, Systole, pycatch22, pyheartlib)
   should stay optional extras and must not be bundled. FeatureDB and ecg_processing have no
   licence, so they can't be reused without permission. The ecg-records engine is
   non-commercial only.
4. **Avoid the MATLAB route.** `pecg` and ECGdeli give strong delineation but need MATLAB or
   the MATLAB Runtime, which conflicts with ECGEN-Eval's pure-Python design.

## 11. Structured catalogue (inputs, sampling rates, features)

The tools above are catalogued in machine-readable form in
`feature_extractors/tools.jsonl` (43 tools, verified from source code on 2026-10-29) against a
canonical feature vocabulary (`feature_extractors/feature_vocab.csv`, 94 features). For each
tool it records the accepted inputs (raw single/multi-lead ECG, WFDB/CSV/EDF files, R peaks or
RR intervals), sampling-rate argument, default, supported range and internal resampling,
minimum duration, amplitude units, and every output mapped to a canonical feature with its
native name and API. `build_db.py` loads it into the `extractor*` tables of the docs Paper
Database (tab **Feature extractors**) and writes `docs/literature/feature_extractors.csv` and
`feature_support_matrix.csv`.

## Sources

- Search and package pages:
  [NeuroKit2](https://pypi.org/project/neurokit2/) ·
  [prominence-delineator](https://pypi.org/project/prominence-delineator) ·
  [PQRSTann](https://pypi.org/project/pqrstann/) ·
  [pecg](https://pypi.org/project/pecg/) ·
  [BioSPPy](https://pypi.org/project/biosppy/) ·
  [FeatureDB](https://github.com/PKUDigitalHealth/FeatureDB) ·
  [pyECGdeli](https://github.com/axel-loewe/pyECGdeli) ·
  [ecg_processing](https://github.com/dieterich-lab/ecg_processing) ·
  [ecg-records](https://pypi.org/project/ecg-records/) ·
  [torch-ecg](https://pypi.org/project/torch-ecg/) ·
  [ecg-segmentation](https://github.com/ckjoung/ecg-segmentation) ·
  [HeartKit](https://github.com/AmbiqAI/heartkit) ·
  [PhysioKit](https://github.com/AmbiqAI/physiokit) ·
  [py-ecg-detectors](https://github.com/berndporr/py-ecg-detectors) ·
  [SleepECG](https://joss.theoj.org/papers/10.21105/joss.05411) ·
  [Systole](https://joss.theoj.org/papers/10.21105/joss.03832) ·
  [hrv-analysis](https://aura-healthcare.github.io/hrv-analysis/) ·
  [pyHRV](https://pyhrv.readthedocs.io/) ·
  [HeartPy](https://python-heart-rate-analysis-toolkit.readthedocs.io/) ·
  [BioPsyKit](https://joss.theoj.org/papers/10.21105/joss.03702) ·
  [physio](https://physio.readthedocs.io/en/latest/overview.html) ·
  [biopeaks](https://pypi.org/project/biopeaks/) ·
  [vital_sqi](https://www.frontiersin.org/articles/10.3389/fphys.2022.1020458/full) ·
  [ECG-featurizer](https://ecg-featurizer.readthedocs.io/) ·
  [pyheartlib](https://joss.theoj.org/papers/10.21105/joss.05792) ·
  [TSFEL](https://pypi.org/project/tsfel) ·
  [ECGomics](https://arxiv.org/abs/2601.15326)
- Benchmarks:
  [Jaeger et al. 2024](https://doi.org/10.1109/ACCESS.2024.3487013) ·
  [Lim et al. 2026](https://arxiv.org/abs/2610.07885) ·
  [Emrich et al. 2024](https://doi.org/10.23919/EUSIPCO63174.2024.10715353) ·
  [FeatureDB wearable validation](https://arxiv.org/abs/2502.17499) ·
  [ECGdeli](https://doi.org/10.1016/j.softx.2020.100639)
- Package metadata: PyPI JSON API and GitHub REST API, queried 2026-10-28.
