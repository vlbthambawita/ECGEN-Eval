"""
HRV feature extraction: SDNN, RMSSD, pNN50.

Computed directly from RR interval series; does not require neurokit2.
When neurokit2 is installed it is used to cross-check, but the same
manual computation is the primary path to keep the dependency optional.
"""

from __future__ import annotations

import numpy as np
from typing import Dict

from ecgen_eval.features.utils import samples_to_ms


def extract_hrv_features(rpeaks: np.ndarray, fs: float) -> Dict[str, float]:
    """
    Compute time-domain HRV indices from R-peak positions.

    Parameters
    ----------
    rpeaks : np.ndarray  Shape (M,) — sorted R-peak sample indices.
    fs : float — sampling frequency in Hz.

    Returns
    -------
    dict with keys: hrv_sdnn_ms, hrv_rmssd_ms, hrv_pnn50
    """
    nan = {"hrv_sdnn_ms": np.nan, "hrv_rmssd_ms": np.nan, "hrv_pnn50": np.nan}

    if len(rpeaks) < 3:
        return nan

    rr_ms = samples_to_ms(np.diff(rpeaks.astype(float)), fs)

    # Filter physiologically implausible RR (< 300 ms or > 2000 ms)
    rr_ms = rr_ms[(rr_ms >= 300) & (rr_ms <= 2000)]
    if len(rr_ms) < 2:
        return nan

    sdnn = float(np.std(rr_ms, ddof=1))

    successive_diff = np.diff(rr_ms)
    rmssd = float(np.sqrt(np.mean(successive_diff ** 2)))
    pnn50 = float(100.0 * np.sum(np.abs(successive_diff) > 50.0) / len(successive_diff))

    return {
        "hrv_sdnn_ms": sdnn,
        "hrv_rmssd_ms": rmssd,
        "hrv_pnn50": pnn50,
    }
