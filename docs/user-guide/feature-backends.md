# How the Extraction Backends Work

ECGEN-Eval measures clinical features in two stages. First a **backend** (the library chosen
with `backend=` / `--feature-backend`) finds the heartbeats and the *fiducial points* of each
beat: R peak, QRS onset and offset, P onset and offset, T peak and T offset. Then the
**feature groups** turn those points into the numbers in `summary_df`. The second stage is the
same code for every backend, so all differences between backends come from where they put
the points.

This page explains, step by step, how each backend finds them. The descriptions follow the
source code of the versions ECGEN-Eval was tested with (NeuroKit2 0.2.12, BioSPPy 2.2.4,
HeartPy 1.2.7). For how to select a backend see
[Clinical Features → Choosing the extraction library](features.md#choosing-the-extraction-library-backend);
for how accurate each one is see the
[backend comparison against GE 12SL](../clinical/index.md#backend-comparison).

## At a glance

| Backend | R peaks | QRS onset / offset | P onset / offset | T peak / offset | Features measured |
|---|---|---|---|---|---|
| `hybrid` *(default)* | NeuroKit2 gradient detector, primary lead | Spatial velocity of **all leads** | NeuroKit2 prominence, every lead, refined to 15 % | NeuroKit2 prominence peak + **tangent** offset, every lead | all |
| `neurokit2` | NeuroKit2 gradient detector, primary lead | `ecg_delineate` (`dwt` by default) | `ecg_delineate` | `ecg_delineate` | all (`peak`: rhythm, HRV only) |
| `scipy` | Pan–Tompkins style, SciPy | Spatial velocity of all leads | — | — | rhythm, HRV, QRS, ST, T amplitude |
| `biosppy` | BioSPPy segmenter (Hamilton by default) | Local extrema of heartbeat templates | Local extrema of templates | Local extrema of templates | all |
| `heartpy` | HeartPy moving-average detector | — | — | — | rhythm, HRV |

## What every backend shares

Whichever backend is used, extraction of one recording runs like this
(`ecgen_eval.features.extractor`):

1. **Choose the primary lead.** `lead_for_intervals` (default `"II"`; the first lead if the
   recording has no lead with that name). The R peaks found on this lead define the beats.
2. **Run the backend.** It returns the R peaks and, for each fiducial type, one value per
   beat (`NaN` when that point was not found). Libraries that only report the points they
   found are lined up with the beats by `align_to_beats`: each point is assigned to the beat
   whose window, bounded by the midpoints between neighbouring R peaks, contains it.
3. **Measure the features** with the selected feature groups:

| Feature | Computed from | How |
|---|---|---|
| `rr_mean_ms`, `rr_std_ms` | R peaks | Mean and standard deviation of the gaps between consecutive R peaks |
| `hr_bpm` | R peaks | 60 000 ÷ `rr_mean_ms` |
| `hrv_sdnn_ms`, `hrv_rmssd_ms`, `hrv_pnn50` | R peaks | RR intervals outside 300–2000 ms are dropped; SDNN (sample SD), RMSSD and pNN50 (%) of the rest |
| `pr_interval_ms` | P onset, QRS onset | QRS onset − P onset, per beat |
| `qrs_duration_ms` | QRS onset, QRS offset | QRS offset − QRS onset, per beat |
| `qt_interval_ms` | QRS onset, T offset | T offset − QRS onset, per beat |
| `p_wave_duration_ms` | P onset, P offset | P offset − P onset, per beat |
| `qtc_bazett_ms` | QT, R peaks | QT ÷ √(mean RR in s) |
| `st_deviation_mv` | QRS onset, QRS offset | Level at QRS offset (J point) + 80 ms minus the PR-segment baseline (median of QRS onset − 40 to − 10 ms), every lead |
| `t_amplitude_mv` | QRS onset, QRS offset, T offset | Signed extreme between J + 80 ms and the T offset (or QRS onset + min(0.6 RR, 550 ms) without a T offset) minus the baseline, every lead |

Per-beat intervals outside a plausible range (PR 60–400 ms, QRS 40–250 ms, QT 200–700 ms,
P 30–200 ms) are treated as delineation errors and dropped; the recording value is the
**median over beats**. ST and T amplitude take the median over beats on each lead and then
the mean over leads. A feature whose points a backend does not provide is `NaN`.

## `hybrid` (default)

The default backend mixes NeuroKit2 with ECGEN-Eval's own multi-lead code
(`ecgen_eval.features.delineation`). It was tuned on PTB-XL against the GE 12SL measurements
and is the most accurate of the five.

1. **Clean the primary lead** with `nk.ecg_clean`: a 5th-order Butterworth high-pass at
   0.5 Hz removes baseline drift, then a 50 Hz power-line filter.
2. **Find the R peaks** with `nk.ecg_peaks(method="neurokit")`. The absolute gradient of the
   signal is smoothed with a 100 ms boxcar; wherever it rises above 1.5 × its 0.75 s moving
   average a QRS complex starts, and where it falls back the complex ends. Complexes shorter
   than 0.4 × the average length are ignored. In each complex the most prominent local maximum
   is the R peak, and peaks closer than 300 ms to the previous one are dropped.
   (`rpeak_method` picks any other `nk.ecg_peaks` method, or `"scipy"` for the detector
   described under [`scipy`](#scipy).)
3. **QRS onset and offset from all leads** (the *spatial velocity*):
    1. Every lead is band-passed 0.5–40 Hz (4th-order Butterworth, zero phase).
    2. The absolute sample-to-sample change is summed over all leads and smoothed over 8 ms.
       This curve is near zero on the flat parts of the ECG and very large during the QRS.
    3. Around each R peak (−150 ms to +200 ms) the *floor* is the 10th percentile of the curve
       and the *peak* its maximum within ±60 ms of R. The threshold is
       floor + 4 % × (peak − floor).
    4. Walking left and right from the R peak, the QRS onset and offset are the first samples
       where the curve drops below the threshold. If either is not reached inside the window
       the beat gets no QRS boundaries.
4. **P wave and T peak on every lead** with NeuroKit2's peak-prominence delineator
   (`nk.ecg_delineate(method="prominence")`, Emrich et al. 2024). Each lead is cleaned and gets
   its own R peaks, then each beat is cut out (from halfway to the previous R peak to halfway
   to the next) and its local maxima and minima are scored by their *prominence* (how far a
   peak stands out from its surroundings, `scipy.signal.peak_prominences`):
    - Q = the most prominent minimum up to 120 ms before R; S = the first prominent minimum
      after R (within 180 ms of Q).
    - **P peak** = the most prominent maximum in the 300 ms before Q. **P onset/offset** = the
      left and right bases of its prominence, searched within 200 ms. ECGEN-Eval then moves
      each base towards the P peak until the wave has risen 15 % of the base-to-peak height,
      because the bases alone sit at the lowest point of the window and make the P wave too
      long.
    - **T peak** = the most prominent maximum *or* minimum at least 150 ms after S, so inverted
      T waves are found too.
5. **T offset by the tangent method** on every lead. The baseline is the median of the signal
   from 40 ms to 8 ms before the QRS onset. Within 150 ms after the T peak, the steepest slope
   back towards the baseline is found; a straight line along that slope is extended to the
   baseline level, and the crossing is the T offset (accepted up to 400 ms after the T peak).
   T waves smaller than 0.02 mV are skipped.
6. **Combine the leads.** Each lead's points are assigned to the primary lead's beats and the
   **median across leads** is taken, beat by beat.

The tangent method ends the T wave earlier than the cardiologist-style "return to baseline",
which is why `hybrid` QT is about 17–20 ms shorter than GE 12SL.

## `neurokit2`

Plain NeuroKit2 with no ECGEN-Eval refinements, for comparison with studies that use
NeuroKit2 directly.

1. **Clean and find R peaks** on the primary lead exactly as in `hybrid` steps 1–2.
2. **Delineate** with `nk.ecg_delineate(method=...)`, by default on the primary lead only.
   With `backend_kwargs={"leads": "all"}` every lead is cleaned and delineated at the primary
   lead's R peaks, and the median across leads is taken per beat.
3. **Map the outputs**: NeuroKit2's `ECG_R_Onsets` / `ECG_R_Offsets` are the QRS onset and
   offset; `ECG_P_Onsets`, `ECG_P_Offsets`, `ECG_T_Peaks` and `ECG_T_Offsets` are used as is.

The four delineation methods (`delineation_method=` / `--delineation-method`):

=== "dwt (default)"

    Discrete wavelet transform, after Martínez et al. (2004).

    1. The signal is resampled to 2000 Hz and decomposed with an *à trous* quadratic-spline
       wavelet into scales 2¹…2⁹. At each scale a wave shows up as a pair of opposite-sign
       peaks, and the wave's peak sits at the zero crossing between them.
    2. **T peak**: zero crossings at scale 2³ in a window after the R peak (from half a QRS
       width to about 0.5 s, shortened at high heart rates). **P peak**: the same at scale 2²
       in the ~0.4 s before the R peak. The candidate with the best score is kept.
    3. **QRS onset**: between the P peak and the Q peak, the last point before the last slope
       maximum where the scale-2² transform is below 50 % of that maximum. **QRS offset**: the
       same between the R peak and the T peak.
    4. **P and T onset/offset**: searching 300 ms before and after each peak (600 ms before
       the T peak; windows shrink at high heart rates), where the transform falls below 40 % of
       the nearest slope maximum (60 % for the T onset).
    5. Q and S peaks come from the `peak` method below.

    The QRS boundaries depend on the P and T peaks being right. On PTB-XL this makes `dwt` QRS
    and PR much less accurate than `hybrid`.

=== "cwt"

    Continuous wavelet transform with the first derivative of a Gaussian (`gaus1`) at scales 1,
    2, 4, 8 and 16.

    1. **P and T peaks**: between consecutive R peaks, significant peaks of the scale-16
       transform are paired, and the ECG maximum within ±50 ms of each zero crossing is a wave
       peak. The first one after R is the T peak and the last one before the next R is the next
       P peak.
    2. **Onsets and offsets**: within 100 ms of each peak, the nearest wavelet modulus maximum is
       found (scale 4 for the QRS, scale 16 for P and T), and the boundary is where the
       transform drops below a fraction of that maximum.

=== "peak"

    Simple rules on each heartbeat segment (`nk.ecg_segment`):

    - Q = the last minimum before the R peak; S = the first minimum after it.
    - P = the highest maximum before Q; T = the highest maximum after S.
    - P onset and T offset from the slope around those peaks.

    There are **no QRS boundaries and no P offset**, so PR, QRS, QT, P duration, ST and T
    amplitude are all `NaN`. Only rhythm and HRV are measured.

=== "prominence"

    The same delineator as in `hybrid` step 4, but used as is: QRS onset/offset are the bases
    of the R-peak prominence (searched within 100 ms), the P boundaries are not refined, and
    the T offset is the right base of the T-peak prominence (within 200 ms) instead of the
    tangent method.

## `scipy`

For environments without NeuroKit2. Only NumPy and SciPy are used.

1. **Find the R peaks** on the primary lead with a Pan–Tompkins style detector
   (`find_r_peaks_scipy`):
    1. 4th-order Butterworth band-pass 5–15 Hz (zero phase), where QRS energy is highest.
    2. Derivative, then square, so steep slopes stand out and are always positive.
    3. Moving-window integration over 150 ms.
    4. Peaks of the integrated signal at least 300 ms apart and above 10 % of its maximum.
    5. Each peak is moved to the largest absolute value of the band-passed signal within
       ±50 ms.
2. **QRS onset and offset** from the spatial velocity of all leads, exactly as `hybrid`
   step 3.
3. No P or T delineation. PR, QT, QTc and P duration are `NaN`. ST deviation and T amplitude
   are still measured, because they need only the QRS points; the T wave is then searched up
   to QRS onset + min(0.6 RR, 550 ms).

## `biosppy`

[BioSPPy](https://github.com/scientisst/BioSPPy) (Bota et al., *SoftwareX* 2024) finds the R
peaks with one of several classic detectors and then reads every wave point off a short
template of each heartbeat.

1. **Filter** each lead as `biosppy.signals.ecg.ecg` does: zero-phase FIR band-pass
   0.67–45 Hz with 1.5 × fs taps (fewer for very short recordings, so the filter fits), then
   the mean is removed. `backend_kwargs={"filtered": False}` only removes the mean.
2. **Find the R peaks** on the primary lead with the segmenter chosen by `rpeak_method`:

    | `rpeak_method` | Algorithm |
    |---|---|
    | `hamilton` *(default)* | Hamilton (2002, EP Limited). Low-pass 25 Hz and high-pass 3 Hz, absolute derivative, 80 ms Hamming smoothing. The threshold sits 47.5 % of the way from the median noise-peak level to the median QRS-peak level, both learned in the first 8 s and updated as beats are found. Peaks within 200 ms of a larger one are ignored, and a search-back looks for missed beats. |
    | `christov` | Christov (2004). Moving averages to suppress power-line and muscle noise, band-pass 9–40 Hz, then a non-linear energy signal. A *combined adaptive threshold* adds a steep-slope term, an integrating term against high-frequency noise and a beat-expectation term that drops as the next beat becomes due. |
    | `engzee` | Engelse and Zeelenberg (1979) with the real-time changes of Lourenço et al. (2012). Differentiator (x[n] − x[n−4]) and a 10-tap low-pass, then thresholds from the maxima and minima of a sliding 1.75 s window. |
    | `gamboa` | Gamboa's detector from BioSPPy. The signal is normalised by its 1st/99th percentiles. Peaks of the negative second derivative above `tol` (0.002) and at least 300 ms apart start a 100 ms window whose maximum is the R peak. |
    | `ssf` | Slope sum function (Zong et al. 2003). Negative slopes are squared, and where they exceed a fixed `threshold` (20) the maximum from 30 ms before to 10 ms after is the R peak. The threshold is absolute, so it suits raw ADC units, not millivolts. |
    | `asi` | Adaptive thresholding with exponential decay (Gutiérrez-Rivas et al. 2015; Sadhukhan and Mitra 2012). Squared double difference, moving integration and a three-state machine (find maximum → wait → decaying threshold). The last second of the recording is ignored, and the wait after each beat is a fixed 50 samples, which is 200 ms only at 250 Hz. |
    | `pantompkins` | Pan–Tompkins++ (Khan and Imtiaz 2022): Pan–Tompkins with an extra filtering stage and adjusted adaptive thresholds. |

3. **Correct the R peaks** (`correct_rpeaks`): each one moves to the largest sample of the
   filtered lead within ±50 ms.
4. **Cut heartbeat templates** (`extract_heartbeats`): for every R peak, the window from 0.2 s
   before to 0.4 s after it. Beats too close to either end of the recording get no template.
5. **Find the wave points on each template** as *local extrema* (`argrelextrema`):

    | Point | BioSPPy function | Rule |
    |---|---|---|
    | QRS onset | `getQPositions` (Q start) | Q = the last local minimum before R; QRS onset = the last local maximum before Q |
    | QRS offset | `getSPositions` (S end) | The first local maximum after R (normally where the S wave ends) |
    | P onset | `getPPositions` (P start) | P peak = the highest point between −0.2 s and −0.04 s; P onset = the last local minimum before it |
    | P offset | `getPPositions` (P end) | The first local minimum between the P peak and −0.04 s |
    | T peak | `getTPositions` | The highest point between +0.14 s and +0.4 s |
    | T offset | `getTPositions` (T end) | The first local minimum after the T peak |

    Some of these functions stop for the whole lead when one beat has no suitable extremum;
    ECGEN-Eval then repeats them one beat at a time so the other beats keep their points.
6. **Combine the leads**: by default only the primary lead is delineated. With
   `backend_kwargs={"leads": "all"}` steps 1 and 4–5 run on every lead at the primary lead's R
   peaks, and the median across leads is taken per beat.

What the rules imply:

- **Any small ripple is an extremum.** The P onset is usually found close to the P peak,
  which makes PR about 35 ms too short on PTB-XL.
- **Missing waves move the boundaries.** Without a Q wave the QRS onset falls back to an
  earlier bump; without an S wave the QRS offset can land on the T wave.
- **T waves are assumed upright and short.** The T peak is the highest point, so an inverted
  T wave is missed, and a T wave ending after +0.4 s has no T offset.
- **Detectors and units.** In our tests on millivolt-scale signals at 500 Hz, `hamilton` and
  `christov` were reliable; `ssf` found no beats (absolute threshold), and `gamboa`, `asi` and
  `pantompkins` sometimes counted beats twice.

## `heartpy`

[HeartPy](https://github.com/paulvangentcom/heartrate_analysis_python) (van Gent et al.,
*JORS* 2019) was built for PPG (pulse) signals. It finds beats but does not delineate waves,
so only heart rate and HRV are measured.

1. **Prepare the primary lead** as HeartPy's documentation recommends for ECG:
    1. Notch filter at 0.05 Hz (`hp.filter_signal(filtertype="notch")`) to remove baseline
       wander.
    2. Scale to 0–1024 (`hp.scale_data`).
    3. Upsample 4× (`scipy.signal.resample`; `upsample=`), because HeartPy's detector prefers
       broad peaks and a QRS complex is narrow.
2. **Detect peaks** (`hp.process`):
    1. Shift the signal so its 0.1th percentile is not negative.
    2. Compute a moving average over 0.75 s (`windowsize=`).
    3. Raise the moving average by a percentage of its mean; each stretch of signal above it is
       one beat, with the peak at its maximum.
    4. Try percentages from 5 % to 300 % and keep the one that gives the steadiest RR series
       (smallest RR standard deviation) with a heart rate between `bpmmin` (40) and `bpmmax`
       (180). If none qualifies, the recording gets no beats.
3. **Reject outliers**: a peak whose RR interval (to the previous peak) differs from the mean
   RR by more than 30 % of the mean or 300 ms, whichever is larger, is marked as rejected. ECGEN-Eval drops rejected peaks unless
   `keep_rejected=True`.
4. **Back to the original sampling rate**: the peaks are divided by the upsampling factor and
   moved to the largest sample of the notch-filtered lead within ±50 ms.

HeartPy computes its own HRV measures, but ECGEN-Eval does not use them: the `rhythm` and
`hrv` groups compute RR, HR, SDNN, RMSSD and pNN50 from the peaks, the same way as for every
backend. Dropping a rejected peak merges two RR intervals into one long one, which lowers the
heart rate of that recording; this is why `heartpy` agrees less with GE 12SL than the others.

## References

- Emrich J. et al. *Physiology-informed ECG delineation based on peak prominence.* EUSIPCO 2024.
- Martínez J.P. et al. *A wavelet-based ECG delineator: evaluation on standard databases.*
  IEEE Trans Biomed Eng 51(4), 2004.
- Makowski D. et al. *NeuroKit2: A Python toolbox for neurophysiological signal processing.*
  Behav Res Methods 53, 2021.
- Pan J., Tompkins W.J. *A real-time QRS detection algorithm.* IEEE Trans Biomed Eng 32(3), 1985.
- Hamilton P.S. *Open Source ECG Analysis Software Documentation.* E.P. Limited, 2002.
- Christov I.I. *Real time electrocardiogram QRS detection using combined adaptive threshold.*
  BioMed Eng OnLine 3:28, 2004.
- Engelse W., Zeelenberg C. *A single scan algorithm for QRS detection and feature
  extraction.* Computers in Cardiology 6, 1979.
- Zong W. et al. *An open-source algorithm to detect onset of arterial blood pressure pulses.*
  Computers in Cardiology 30, 2003.
- Gutiérrez-Rivas R. et al. *Novel real-time low-complexity QRS complex detector based on
  adaptive thresholding.* IEEE Sensors J 15(10), 2015.
- Khan N., Imtiaz M.N. *Pan-Tompkins++: A robust approach to detect R-peaks in ECG signals.*
  arXiv:2211.03171, 2022.
- Bota P. et al. *BioSPPy: A Python toolbox for physiological signal processing.* SoftwareX,
  2024. [doi:10.1016/j.softx.2024.101712](https://doi.org/10.1016/j.softx.2024.101712)
- van Gent P. et al. *HeartPy: A novel heart rate algorithm for the analysis of noisy
  signals.* J Open Res Softw 7(1), 2019.
  [doi:10.5334/jors.241](https://doi.org/10.5334/jors.241)
