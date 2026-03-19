"""
Interval feature extraction: RR, HR, PR, QRS, QT, QTc, P-wave duration.

When neurokit2 delineation is available (waves dict), we use the boundary
indices it provides.  When it is None we fall back to heuristic estimates
based on R-peak positions alone, which are rougher but still meaningful for
distribution-level comparisons between real and synthetic ECG.
"""

from __future__ import annotations

import numpy as np
from typing import Dict, List, Optional

from ecgen_eval.features.utils import samples_to_ms, ms_to_samples


# ------------------------------------------------------------------ #
# RR and HR                                                           #
# ------------------------------------------------------------------ #

def extract_rr_hr(rpeaks: np.ndarray, fs: float) -> Dict[str, float]:
    """RR intervals (ms) and heart rate (bpm) from R-peak positions."""
    if len(rpeaks) < 2:
        return {
            "rr_mean_ms": np.nan,
            "rr_std_ms": np.nan,
            "hr_bpm": np.nan,
        }
    rr_samples = np.diff(rpeaks)
    rr_ms = samples_to_ms(rr_samples, fs)
    hr = 60_000.0 / np.mean(rr_ms) if np.mean(rr_ms) > 0 else np.nan
    return {
        "rr_mean_ms": float(np.mean(rr_ms)),
        "rr_std_ms": float(np.std(rr_ms)),
        "hr_bpm": float(hr),
    }


# ------------------------------------------------------------------ #
# Interval features — neurokit2 path                                  #
# ------------------------------------------------------------------ #

def _safe_mean_ms(indices: Optional[List], fs: float) -> float:
    """Mean of (possibly None-filled) delineation index list → ms."""
    if indices is None:
        return np.nan
    arr = np.array([v for v in indices if v is not None and not np.isnan(float(v))], dtype=float)
    if len(arr) == 0:
        return np.nan
    return float(np.mean(arr) / fs * 1000.0)


def _interval_ms_nk(onset_key: str, offset_key: str, waves: dict, fs: float) -> float:
    """Compute mean interval in ms from onset/offset index arrays in waves dict."""
    onsets = waves.get(onset_key, None)
    offsets = waves.get(offset_key, None)
    if onsets is None or offsets is None:
        return np.nan
    pairs = [
        (float(a), float(b))
        for a, b in zip(onsets, offsets)
        if a is not None and b is not None and not np.isnan(float(a)) and not np.isnan(float(b))
    ]
    if not pairs:
        return np.nan
    intervals = [(b - a) / fs * 1000.0 for a, b in pairs]
    return float(np.mean([v for v in intervals if v > 0]))


# ------------------------------------------------------------------ #
# Heuristic fallback intervals                                         #
# ------------------------------------------------------------------ #
# These assume a "normal" ECG morphology with typical timing.
# Heuristic offsets (ms from R-peak):
#   QRS onset  ≈ R - 50 ms
#   QRS offset ≈ R + 60 ms  (J-point)
#   T-peak     ≈ R + 200 ms
#   T-end      ≈ R + 350 ms
#   P-peak     ≈ R - 180 ms
#   P-onset    ≈ R - 230 ms
#   P-end      ≈ R - 140 ms

_QRS_ONSET_MS  = -50.0
_QRS_OFFSET_MS =  60.0
_T_END_MS      = 350.0
_P_ONSET_MS    = -230.0
_P_END_MS      = -140.0


def extract_interval_features(
    signal: np.ndarray,
    fs: float,
    rpeaks: np.ndarray,
    waves: Optional[dict] = None,
) -> Dict[str, float]:
    """
    Extract PR, QRS, QT, QTc, and P-wave duration.

    Parameters
    ----------
    signal : (T,)  Single-lead ECG.
    fs : float
    rpeaks : (M,) R-peak sample indices.
    waves : dict or None  Neurokit2 delineation result.

    Returns
    -------
    dict with keys: pr_interval_ms, qrs_duration_ms, qt_interval_ms,
                    qtc_bazett_ms, p_wave_duration_ms
    """
    rr = extract_rr_hr(rpeaks, fs)
    rr_s = rr["rr_mean_ms"] / 1000.0 if not np.isnan(rr["rr_mean_ms"]) else np.nan

    if waves is not None:
        # neurokit2 delineation
        qrs_dur = _interval_ms_nk("ECG_Q_Peaks", "ECG_S_Peaks", waves, fs)
        if np.isnan(qrs_dur):
            qrs_dur = _interval_ms_nk("ECG_QRS_Onsets", "ECG_QRS_Offsets", waves, fs)

        qt = _interval_ms_nk("ECG_QRS_Onsets", "ECG_T_Offsets", waves, fs)
        pr = _interval_ms_nk("ECG_P_Onsets", "ECG_QRS_Onsets", waves, fs)
        p_dur = _interval_ms_nk("ECG_P_Onsets", "ECG_P_Offsets", waves, fs)
    else:
        # Heuristic fallback
        qrs_dur = _QRS_OFFSET_MS - _QRS_ONSET_MS   # ~110 ms
        qt = _T_END_MS - _QRS_ONSET_MS              # ~400 ms
        pr = -_QRS_ONSET_MS + (_P_ONSET_MS - _P_END_MS) / 2  # rough
        p_dur = _P_END_MS - _P_ONSET_MS             # ~90 ms

        # Modulate with actual signal length: cap implausible values
        if qrs_dur < 0 or qrs_dur > 300:
            qrs_dur = np.nan
        if qt < 0 or qt > 700:
            qt = np.nan

    # QTc (Bazett): QT / sqrt(RR_s)
    if not np.isnan(qt) and not np.isnan(rr_s) and rr_s > 0:
        qtc = qt / np.sqrt(rr_s)
    else:
        qtc = np.nan

    return {
        "pr_interval_ms": float(pr),
        "qrs_duration_ms": float(qrs_dur),
        "qt_interval_ms": float(qt),
        "qtc_bazett_ms": float(qtc),
        "p_wave_duration_ms": float(p_dur),
    }
