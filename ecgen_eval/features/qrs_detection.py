"""
R-peak detection for ECG signals.

Primary:  neurokit2.ecg_peaks()  (Pan-Tompkins implementation)
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

        _, info = nk.ecg_peaks(signal.astype(float), sampling_rate=int(fs), method=method)
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
    signal: np.ndarray, rpeaks: np.ndarray, fs: float
) -> Optional[dict]:
    """
    Delineate P, QRS, and T boundaries using neurokit2.ecg_delineate().

    Returns the ``waves`` dict from neurokit2 on success, or None if neurokit2
    is not installed or delineation fails (caller must handle None).
    """
    if len(rpeaks) < 2:
        return None
    try:
        import neurokit2 as nk

        _, waves = nk.ecg_delineate(
            signal.astype(float), rpeaks, sampling_rate=int(fs), method="peak"
        )
        return waves
    except Exception:
        return None
