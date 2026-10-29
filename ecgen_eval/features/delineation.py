"""
Beat delineation: QRS, P and T boundaries for every beat of a recording.

Two complementary methods are combined:

- **QRS onset / offset** come from the *spatial velocity* of all leads (sum of the absolute
  slopes), the classic multi-lead approach of commercial 12-lead programs. For each beat the
  QRS spans the samples around the R peak where the velocity stays above
  ``baseline + QRS_THRESHOLD * (peak - baseline)``. This needs only NumPy (and SciPy for
  filtering), so QRS duration is available without NeuroKit2.
- **P onset / offset and T peak / offset** come from NeuroKit2's peak-prominence delineator
  (``nk.ecg_delineate(method="prominence")``, Emrich et al., EUSIPCO 2024), run on every lead
  with that lead's own R peaks. Its P boundaries are the lowest points of a fixed window, so
  they are refined towards the P peak to where the wave exceeds ``P_BOUNDARY_FRACTION`` of its
  amplitude. The T offset uses the **tangent method**: the steepest return of the T wave
  towards the baseline is extended to the baseline level (the PR segment just before the QRS
  onset). The per-lead points are assigned to the reference beats and combined with the
  median across leads.

All fiducial arrays returned here are aligned with the reference R peaks: element ``i``
belongs to beat ``i`` and is NaN when it could not be found. Validated against the GE 12SL
global measurements of PTB-XL+ (see the Clinical Features Explained docs).
"""

from __future__ import annotations

import numpy as np
from typing import Dict, Optional

from ecgen_eval.features.utils import bandpass_filter

#: Fraction of the (peak - baseline) spatial velocity that delimits the QRS complex.
QRS_THRESHOLD = 0.04

# Search windows around each R peak (ms).
_QRS_SEARCH_BEFORE_MS = 150
_QRS_SEARCH_AFTER_MS = 200
_QRS_CORE_MS = 60          # the velocity peak is taken within R +/- this
_VELOCITY_SMOOTH_MS = 8

#: Extra keyword arguments for ``nk.ecg_delineate(method="prominence")`` (window lengths in
#: ms within which wave boundaries are searched).
PROMINENCE_KWARGS: Dict[str, float] = {"max_p_basepoint_interval": 200}

#: P onset/offset = first sample (from the window base towards the P peak) where the wave
#: exceeds this fraction of the base-to-peak amplitude.
P_BOUNDARY_FRACTION = 0.15

# Tangent-method T offset: steepest descent searched within 150 ms after the T peak, offset
# accepted up to 400 ms after it; T waves smaller than 0.02 mV are skipped.
_T_SLOPE_SEARCH_MS = 150
_T_OFFSET_MAX_MS = 400
_T_MIN_AMPLITUDE = 0.02
_BASELINE_START_MS = 40
_BASELINE_END_MS = 8

#: NeuroKit2 delineation outputs that are combined across leads.
NK_KEYS = ("ECG_P_Onsets", "ECG_P_Offsets", "ECG_T_Peaks", "ECG_T_Offsets")


def align_to_beats(values, rpeaks: np.ndarray) -> np.ndarray:
    """
    Assign fiducial sample indices to beats.

    NeuroKit2 drops missing or non-positive points, so its output lists are not always aligned
    with the R peaks. Each value is assigned to the beat whose window, bounded by the midpoints
    between consecutive R peaks, contains it; the first value per beat wins.

    Returns a float array of length ``len(rpeaks)`` with NaN for beats without a value.
    """
    out = np.full(len(rpeaks), np.nan)
    if len(rpeaks) == 0 or values is None:
        return out
    mids = (np.asarray(rpeaks[:-1], dtype=float) + np.asarray(rpeaks[1:], dtype=float)) / 2
    for v in values:
        try:
            v = float(v)
        except (TypeError, ValueError):
            continue
        if not np.isfinite(v):
            continue
        b = int(np.searchsorted(mids, v))
        if np.isnan(out[b]):
            out[b] = v
    return out


def qrs_boundaries(
    recording: np.ndarray, rpeaks: np.ndarray, fs: float, threshold: float = QRS_THRESHOLD
) -> Dict[str, np.ndarray]:
    """
    QRS onset and offset of every beat from the spatial velocity of all leads.

    Parameters
    ----------
    recording : (L, T) or (T,) ECG.
    rpeaks : (M,) reference R-peak sample indices.
    fs : float
    threshold : float
        Fraction of the velocity range above the beat's baseline that counts as QRS.

    Returns
    -------
    dict with ``ECG_QRS_Onsets`` and ``ECG_QRS_Offsets`` (float arrays aligned with rpeaks).
    """
    rec = np.atleast_2d(np.asarray(recording, dtype=float))
    rpeaks = np.asarray(rpeaks, dtype=int)
    onsets = np.full(len(rpeaks), np.nan)
    offsets = np.full(len(rpeaks), np.nan)
    if len(rpeaks) == 0 or rec.shape[1] < 3:
        return {"ECG_QRS_Onsets": onsets, "ECG_QRS_Offsets": offsets}

    filt = np.stack([bandpass_filter(x, fs, 0.5, 40.0) for x in rec])
    vel = np.abs(np.diff(filt, axis=1)).sum(axis=0)
    k = max(1, int(round(_VELOCITY_SMOOTH_MS / 1000.0 * fs)))
    vel = np.convolve(vel, np.ones(k) / k, mode="same")

    before = int(_QRS_SEARCH_BEFORE_MS / 1000.0 * fs)
    after = int(_QRS_SEARCH_AFTER_MS / 1000.0 * fs)
    core = max(1, int(_QRS_CORE_MS / 1000.0 * fs))
    for i, r in enumerate(rpeaks):
        lo, hi = r - before, r + after
        if lo < 0 or hi >= len(vel):
            continue
        floor = np.percentile(vel[lo:hi], 10)
        peak = vel[max(lo, r - core): r + core].max()
        if peak <= floor:
            continue
        th = floor + threshold * (peak - floor)
        on = r
        while on > lo and vel[on] > th:
            on -= 1
        off = r
        while off < hi and vel[off] > th:
            off += 1
        if on > lo and off < hi:  # both boundaries found inside the search window
            onsets[i], offsets[i] = on, off
    return {"ECG_QRS_Onsets": onsets, "ECG_QRS_Offsets": offsets}


def _refine_boundary(sig: np.ndarray, peak: float, base: float, fraction: float) -> float:
    """Walk from ``base`` towards ``peak`` until the signal exceeds ``fraction`` of the rise."""
    if not (np.isfinite(peak) and np.isfinite(base)):
        return np.nan
    peak, base = int(peak), int(base)
    rise = sig[peak] - sig[base]
    if rise == 0:
        return np.nan
    step = 1 if peak > base else -1
    i = base
    while i != peak and (sig[i] - sig[base]) / rise <= fraction:
        i += step
    return float(i)


def _tangent_t_offset(sig: np.ndarray, t_peak: float, qrs_onset: float, fs: float) -> float:
    """T offset where the steepest T downslope, extended as a line, meets the baseline."""
    if not (np.isfinite(t_peak) and np.isfinite(qrs_onset)):
        return np.nan
    t, qo = int(t_peak), int(qrs_onset)
    b0 = qo - int(_BASELINE_START_MS / 1000.0 * fs)
    b1 = qo - int(_BASELINE_END_MS / 1000.0 * fs)
    end = t + int(_T_SLOPE_SEARCH_MS / 1000.0 * fs)
    if b0 < 0 or end >= len(sig) or b1 <= b0:
        return np.nan
    baseline = float(np.median(sig[b0:b1]))
    amp = sig[t] - baseline
    if abs(amp) < _T_MIN_AMPLITUDE:
        return np.nan
    slope = np.diff(sig[t:end + 1])
    k = int(np.argmax(-np.sign(amp) * slope))  # steepest return towards the baseline
    if slope[k] == 0 or np.sign(slope[k]) == np.sign(amp):
        return np.nan
    x = t + k + (baseline - sig[t + k]) / slope[k]
    return float(x) if t < x < t + _T_OFFSET_MAX_MS / 1000.0 * fs else np.nan


def _nk_lead_fiducials(
    signal: np.ndarray, rpeaks: np.ndarray, fs: float, method: str, qrs_onsets: np.ndarray
):
    """P/T fiducials of one lead (own R peaks), aligned to the reference beats."""
    import neurokit2 as nk

    clean = nk.ecg_clean(signal, sampling_rate=int(fs))
    _, info = nk.ecg_peaks(clean, sampling_rate=int(fs))
    own = np.asarray(info["ECG_R_Peaks"], dtype=int)
    if len(own) < 2:
        return None
    kwargs = PROMINENCE_KWARGS if method == "prominence" else {}
    _, waves = nk.ecg_delineate(clean, own, sampling_rate=int(fs), method=method, **kwargs)
    out = {k: align_to_beats(waves.get(k), rpeaks) for k in NK_KEYS}
    if method == "prominence":
        p_peaks = align_to_beats(waves.get("ECG_P_Peaks"), rpeaks)
        for key in ("ECG_P_Onsets", "ECG_P_Offsets"):
            out[key] = np.array([_refine_boundary(clean, pk, b, P_BOUNDARY_FRACTION)
                                 for pk, b in zip(p_peaks, out[key])])
    out["ECG_T_Offsets"] = np.array([_tangent_t_offset(clean, tp, qo, fs)
                                     for tp, qo in zip(out["ECG_T_Peaks"], qrs_onsets)])
    return out


def delineate_recording(
    recording: np.ndarray,
    rpeaks: np.ndarray,
    fs: float,
    method: str = "prominence",
) -> Optional[Dict[str, np.ndarray]]:
    """
    Delineate every beat of a recording.

    Parameters
    ----------
    recording : (L, T) or (T,) ECG.
    rpeaks : (M,) reference R-peak sample indices (from the primary lead).
    fs : float
    method : str
        NeuroKit2 ``ecg_delineate`` method for the P and T waves (default ``"prominence"``).

    Returns
    -------
    dict of arrays aligned with ``rpeaks``: ``ECG_QRS_Onsets``, ``ECG_QRS_Offsets`` and, when
    NeuroKit2 is installed, ``ECG_P_Onsets``, ``ECG_P_Offsets``, ``ECG_T_Peaks``,
    ``ECG_T_Offsets`` (median across leads). ``None`` when there are fewer than 2 R peaks.
    """
    rec = np.atleast_2d(np.asarray(recording, dtype=float))
    rpeaks = np.asarray(rpeaks, dtype=int)
    if len(rpeaks) < 2:
        return None
    fid = qrs_boundaries(rec, rpeaks, fs)

    try:
        import neurokit2  # noqa: F401
    except ImportError:
        return fid

    per_lead = {k: [] for k in NK_KEYS}
    for lead in rec:
        try:
            lf = _nk_lead_fiducials(lead, rpeaks, fs, method, fid["ECG_QRS_Onsets"])
        except Exception:  # flat / too short / delineation failure on this lead
            lf = None
        if lf is None:
            continue
        for k in NK_KEYS:
            per_lead[k].append(lf[k])
    for k in NK_KEYS:
        if per_lead[k]:
            stack = np.stack(per_lead[k])
            with np.errstate(all="ignore"):
                fid[k] = np.array([np.nanmedian(c) if np.isfinite(c).any() else np.nan
                                   for c in stack.T])
        else:
            fid[k] = np.full(len(rpeaks), np.nan)
    return fid
