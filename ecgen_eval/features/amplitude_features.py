"""
Amplitude feature extraction: ST deviation, T-wave amplitude.

Both are measured per beat against the beat's baseline, the median level of the PR segment
just before the QRS onset ([QRS onset - 40 ms, QRS onset - 10 ms]):

- ST deviation = signal at the J point (QRS offset) + 80 ms - baseline.
- T amplitude = signed extreme of the T wave (the sample furthest from the baseline) between
  J + 80 ms and the T offset (or QRS onset + min(0.6 RR, 550 ms) when the T offset is unknown).

The recording value is the median over beats. Fiducials come from
:func:`ecgen_eval.features.delineation.delineate_recording`, so leads of a recording share the
same beat timing.
"""

from __future__ import annotations

import numpy as np
from typing import Dict, Optional

from ecgen_eval.features.utils import ms_to_samples

_BASELINE_START_MS = 40   # baseline window: [QRS onset - 40 ms, QRS onset - 10 ms]
_BASELINE_END_MS = 10
_ST_AFTER_J_MS = 80       # ST level read at J + 80 ms
_T_MAX_AFTER_ONSET_MS = 550
_T_MAX_RR_FRACTION = 0.6


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
    waves : dict or None
        Fiducials aligned with ``rpeaks`` (from ``delineate_recording``); computed from this
        lead alone when None.

    Returns
    -------
    dict with keys: st_deviation_mv, t_amplitude_mv
    """
    nan = {"st_deviation_mv": np.nan, "t_amplitude_mv": np.nan}
    rpeaks = np.asarray(rpeaks, dtype=int)
    if len(rpeaks) < 2:
        return nan
    if waves is None:
        from ecgen_eval.features.delineation import delineate_recording

        waves = delineate_recording(signal, rpeaks, fs)
    if not waves:
        return nan

    sig = np.asarray(signal, dtype=float)
    n = len(sig)
    on = np.asarray(waves["ECG_QRS_Onsets"], dtype=float)
    off = np.asarray(waves["ECG_QRS_Offsets"], dtype=float)
    t_off = np.asarray(waves.get("ECG_T_Offsets", np.full(len(rpeaks), np.nan)), dtype=float)
    rr = np.diff(rpeaks)
    rr = np.append(rr, rr[-1])

    b0, b1 = ms_to_samples(_BASELINE_START_MS, fs), ms_to_samples(_BASELINE_END_MS, fs)
    st_gap = ms_to_samples(_ST_AFTER_J_MS, fs)
    t_cap = ms_to_samples(_T_MAX_AFTER_ONSET_MS, fs)

    st_vals, t_vals = [], []
    for i in range(len(rpeaks)):
        if not (np.isfinite(on[i]) and np.isfinite(off[i])):
            continue
        qo, j = int(on[i]), int(off[i])
        if qo - b0 < 0:
            continue
        baseline = float(np.median(sig[qo - b0: qo - b1 + 1]))
        st_pt = j + st_gap
        if st_pt < n:
            st_vals.append(sig[st_pt] - baseline)
        end = qo + min(t_cap, int(_T_MAX_RR_FRACTION * rr[i]))
        if np.isfinite(t_off[i]) and st_pt < t_off[i] <= end + t_cap:
            end = int(t_off[i])
        end = min(end, n - 1)
        if end > st_pt:
            seg = sig[st_pt: end + 1] - baseline
            t_vals.append(float(seg[np.argmax(np.abs(seg))]))

    return {
        "st_deviation_mv": float(np.median(st_vals)) if st_vals else np.nan,
        "t_amplitude_mv": float(np.median(t_vals)) if t_vals else np.nan,
    }
