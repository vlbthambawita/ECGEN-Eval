"""Shared helpers for ECG feature extraction (filtering, peak refinement)."""

from __future__ import annotations

import numpy as np
from typing import Tuple


def bandpass_filter(signal: np.ndarray, fs: float, low: float = 0.5, high: float = 40.0) -> np.ndarray:
    """4th-order Butterworth bandpass filter. Falls back to identity if scipy absent."""
    try:
        from scipy.signal import butter, filtfilt

        nyq = fs / 2.0
        lo = max(low / nyq, 1e-6)
        hi = min(high / nyq, 1.0 - 1e-6)
        b, a = butter(4, [lo, hi], btype="band")
        return filtfilt(b, a, signal.astype(np.float64)).astype(signal.dtype)
    except ImportError:
        return signal


def find_r_peaks_scipy(signal: np.ndarray, fs: float) -> np.ndarray:
    """
    Pan-Tompkins-inspired R-peak detector using scipy.signal.find_peaks.

    Steps: bandpass (5–15 Hz) → derivative → square → moving-window integrate
    → find_peaks with minimum RR distance of 300 ms → refine on filtered signal.
    Returns array of sample indices.
    """
    try:
        from scipy.signal import butter, filtfilt, find_peaks

        sig = signal.astype(np.float64)
        nyq = fs / 2.0
        b, a = butter(4, [5.0 / nyq, 15.0 / nyq], btype="band")
        filt = filtfilt(b, a, sig)

        diff = np.gradient(filt)
        squared = diff ** 2
        win = max(1, int(0.15 * fs))
        integrated = np.convolve(squared, np.ones(win) / win, mode="same")

        min_dist = max(1, int(0.3 * fs))  # 300 ms
        peaks, _ = find_peaks(integrated, distance=min_dist, height=0.1 * np.max(integrated))

        # Refine: snap to max of |filt| within ±50 ms
        refine = max(1, int(0.05 * fs))
        refined = []
        for p in peaks:
            lo = max(0, p - refine)
            hi = min(len(filt), p + refine + 1)
            refined.append(lo + int(np.argmax(np.abs(filt[lo:hi]))))
        return np.array(refined, dtype=int)

    except ImportError:
        # Minimal fallback: threshold at 60% of max, spaced ≥300 ms apart
        threshold = 0.6 * float(np.max(np.abs(signal)))
        above = (np.abs(signal) > threshold).astype(int)
        crossings = np.where(np.diff(above) == 1)[0]
        if len(crossings) == 0:
            return np.array([], dtype=int)
        min_dist = int(0.3 * fs)
        peaks = [int(crossings[0])]
        for c in crossings[1:]:
            if c - peaks[-1] >= min_dist:
                peaks.append(int(c))
        return np.array(peaks, dtype=int)


def ms_to_samples(ms: float, fs: float) -> int:
    return max(1, int(ms / 1000.0 * fs))


def samples_to_ms(samples: int, fs: float) -> float:
    return samples / fs * 1000.0
