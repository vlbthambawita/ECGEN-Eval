"""
Amplitude feature extraction: ST deviation, T-wave amplitude.

Uses neurokit2 delineation when available; otherwise applies heuristic
windows around R-peaks.
"""

from __future__ import annotations

import numpy as np
from typing import Dict, Optional

from ecgen_eval.features.utils import ms_to_samples


# Heuristic offsets (ms from R-peak)
_J_POINT_MS      =  80   # J-point (end of QRS)
_ST_MEASURE_MS   = 120   # ST level measured here (80 ms after J-point standard)
_T_WINDOW_START  = 100   # T-wave search window start (ms after R)
_T_WINDOW_END    = 400   # T-wave search window end (ms after R)
_ISOELECTRIC_PRE = 200   # ms before R for baseline estimation (PQ segment)
_ISOELECTRIC_POST =  50  # endpoint of baseline window (ms before R)


def _isoelectric_level(signal: np.ndarray, rpeaks: np.ndarray, fs: float) -> float:
    """
    Estimate the isoelectric (baseline) voltage as the median of the PQ segment
    across all beats.  Window: [R - 200 ms, R - 50 ms].
    """
    pre = ms_to_samples(_ISOELECTRIC_PRE, fs)
    post = ms_to_samples(_ISOELECTRIC_POST, fs)
    segments = []
    for r in rpeaks:
        lo = r - pre
        hi = r - post
        if lo >= 0 and hi < len(signal) and hi > lo:
            segments.append(np.median(signal[lo:hi]))
    if segments:
        return float(np.median(segments))
    return 0.0


def extract_amplitude_features(
    signal: np.ndarray,
    fs: float,
    rpeaks: np.ndarray,
    waves: Optional[dict] = None,
) -> Dict[str, float]:
    """
    Extract ST deviation and T-wave amplitude for one lead.

    Parameters
    ----------
    signal : (T,) Single-lead ECG (mV).
    fs : float
    rpeaks : (M,) R-peak sample indices.
    waves : dict or None  Neurokit2 delineation result.

    Returns
    -------
    dict with keys: st_deviation_mv, t_amplitude_mv
    """
    if len(rpeaks) == 0:
        return {"st_deviation_mv": np.nan, "t_amplitude_mv": np.nan}

    baseline = _isoelectric_level(signal, rpeaks, fs)

    # ---- T-wave amplitude ---- #
    if waves is not None:
        t_peaks = waves.get("ECG_T_Peaks", None)
        if t_peaks is not None:
            vals = [
                signal[int(p)] - baseline
                for p in t_peaks
                if p is not None and not np.isnan(float(p)) and 0 <= int(p) < len(signal)
            ]
            t_amp = float(np.mean(vals)) if vals else np.nan
        else:
            t_amp = np.nan
    else:
        # Heuristic: search for maximum in T-wave window after each R
        t_start = ms_to_samples(_T_WINDOW_START, fs)
        t_end = ms_to_samples(_T_WINDOW_END, fs)
        vals = []
        for r in rpeaks:
            lo = r + t_start
            hi = r + t_end
            if hi < len(signal):
                peak_val = float(np.max(signal[lo:hi]) - baseline)
                vals.append(peak_val)
        t_amp = float(np.mean(vals)) if vals else np.nan

    # ---- ST deviation ---- #
    if waves is not None:
        j_points = waves.get("ECG_QRS_Offsets", None)
        if j_points is not None:
            st_window = ms_to_samples(80, fs)  # 80 ms after J-point
            st_vals = []
            for j in j_points:
                if j is None or np.isnan(float(j)):
                    continue
                j = int(j)
                measure_pt = j + st_window
                if measure_pt < len(signal):
                    st_vals.append(float(signal[measure_pt]) - baseline)
            st_dev = float(np.mean(st_vals)) if st_vals else np.nan
        else:
            st_dev = np.nan
    else:
        # Heuristic: measure at fixed offset after R-peak
        st_pt = ms_to_samples(_ST_MEASURE_MS, fs)
        vals = []
        for r in rpeaks:
            pt = r + st_pt
            if pt < len(signal):
                vals.append(float(signal[pt]) - baseline)
        st_dev = float(np.mean(vals)) if vals else np.nan

    return {
        "st_deviation_mv": st_dev,
        "t_amplitude_mv": t_amp,
    }
