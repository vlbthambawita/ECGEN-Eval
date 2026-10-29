"""
R-peak detection for ECG signals.

Primary:  neurokit2.ecg_clean() + neurokit2.ecg_peaks()
Fallback: scipy-based implementation in ecgen_eval.features.utils
"""

from __future__ import annotations

import numpy as np
from typing import Optional


def detect_rpeaks(signal: np.ndarray, fs: float, method: str = "neurokit") -> np.ndarray:
    """
    Detect R-peak sample indices in a single-lead ECG signal.

    Parameters
    ----------
    signal : np.ndarray  shape (T,)
        Single-lead ECG time series.
    fs : float
        Sampling frequency in Hz.
    method : str
        Passed to neurokit2.ecg_peaks(). Ignored if neurokit2 unavailable.

    Returns
    -------
    np.ndarray of int  — R-peak sample indices, sorted ascending.
    """
    if signal.ndim != 1:
        raise ValueError(f"Expected 1-D signal, got shape {signal.shape}")

    try:
        import neurokit2 as nk  # optional dependency

        clean = nk.ecg_clean(signal.astype(float), sampling_rate=int(fs))
        _, info = nk.ecg_peaks(clean, sampling_rate=int(fs), method=method)
        peaks = np.asarray(info["ECG_R_Peaks"], dtype=int)
        return peaks[peaks >= 0]
    except ImportError:
        from ecgen_eval.features.utils import find_r_peaks_scipy

        return find_r_peaks_scipy(signal, fs)
    except Exception:
        # neurokit2 present but failed (e.g. signal too short/flat)
        from ecgen_eval.features.utils import find_r_peaks_scipy

        return find_r_peaks_scipy(signal, fs)


def delineate_ecg(
    signal: np.ndarray, rpeaks: np.ndarray, fs: float, method: str = "prominence"
) -> Optional[dict]:
    """
    Delineate P, QRS and T boundaries of a single-lead ECG.

    Thin wrapper around :func:`ecgen_eval.features.delineation.delineate_recording`; returns
    fiducial arrays aligned with ``rpeaks``, or None when there are fewer than 2 R peaks.
    """
    from ecgen_eval.features.delineation import delineate_recording

    try:
        return delineate_recording(signal, rpeaks, fs, method=method)
    except Exception:
        return None
