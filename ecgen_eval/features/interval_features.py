"""
Interval feature extraction: RR, HR, PR, QRS, QT, QTc, P-wave duration.

Intervals are computed per beat from the aligned fiducial points of
:func:`ecgen_eval.features.delineation.delineate_recording`, checked against plausible
physiological ranges, and summarised with the median over beats:

- PR  = QRS onset - P onset
- QRS = QRS offset - QRS onset
- QT  = T offset - QRS onset;  QTc (Bazett) = QT / sqrt(mean RR in s)
- P duration = P offset - P onset

QRS onset/offset need only NumPy/SciPy; the P and T points need NeuroKit2. Features whose
points are missing are NaN (there are no fixed placeholder values).
"""

from __future__ import annotations

import numpy as np
from typing import Dict, Optional

from ecgen_eval.features.utils import samples_to_ms


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
# Interval features from aligned fiducials                            #
# ------------------------------------------------------------------ #

#: Plausible range (ms) per interval; beats outside it are treated as delineation errors.
INTERVAL_BOUNDS_MS = {
    "pr_interval_ms": (60.0, 400.0),
    "qrs_duration_ms": (40.0, 250.0),
    "qt_interval_ms": (200.0, 700.0),
    "p_wave_duration_ms": (30.0, 200.0),
}

_INTERVAL_POINTS = {
    "pr_interval_ms": ("ECG_P_Onsets", "ECG_QRS_Onsets"),
    "qrs_duration_ms": ("ECG_QRS_Onsets", "ECG_QRS_Offsets"),
    "qt_interval_ms": ("ECG_QRS_Onsets", "ECG_T_Offsets"),
    "p_wave_duration_ms": ("ECG_P_Onsets", "ECG_P_Offsets"),
}


def beat_intervals(waves: Optional[dict], fs: float) -> Dict[str, np.ndarray]:
    """Per-beat intervals (ms, NaN where missing or implausible) from aligned fiducials."""
    out = {}
    for name, (start, end) in _INTERVAL_POINTS.items():
        if not waves or start not in waves or end not in waves:
            out[name] = np.array([])
            continue
        a = np.asarray(waves[start], dtype=float)
        b = np.asarray(waves[end], dtype=float)
        ms = (b - a) / fs * 1000.0
        lo, hi = INTERVAL_BOUNDS_MS[name]
        with np.errstate(invalid="ignore"):
            out[name] = np.where((ms >= lo) & (ms <= hi), ms, np.nan)
    return out


def _median(values: np.ndarray) -> float:
    values = values[np.isfinite(values)] if len(values) else values
    return float(np.median(values)) if len(values) else np.nan


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
    signal : (T,) or (L, T) ECG; only used to delineate when ``waves`` is None.
    fs : float
    rpeaks : (M,) R-peak sample indices.
    waves : dict or None
        Fiducials aligned with ``rpeaks`` (from ``delineate_recording``). When None, the
        signal is delineated here.

    Returns
    -------
    dict with keys: pr_interval_ms, qrs_duration_ms, qt_interval_ms,
                    qtc_bazett_ms, p_wave_duration_ms
    """
    if waves is None and len(rpeaks) >= 2:
        from ecgen_eval.features.delineation import delineate_recording

        waves = delineate_recording(signal, rpeaks, fs)

    per_beat = beat_intervals(waves, fs)
    feats = {name: _median(v) for name, v in per_beat.items()}

    rr = extract_rr_hr(rpeaks, fs)
    rr_s = rr["rr_mean_ms"] / 1000.0
    qt = feats["qt_interval_ms"]
    qtc = qt / np.sqrt(rr_s) if np.isfinite(qt) and np.isfinite(rr_s) and rr_s > 0 else np.nan

    return {
        "pr_interval_ms": feats["pr_interval_ms"],
        "qrs_duration_ms": feats["qrs_duration_ms"],
        "qt_interval_ms": qt,
        "qtc_bazett_ms": float(qtc),
        "p_wave_duration_ms": feats["p_wave_duration_ms"],
    }
