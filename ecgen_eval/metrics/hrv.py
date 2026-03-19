"""
Heart Rate Variability (HRV) statistics comparison for ECG evaluation.

Reference
---------
Task Force of the European Society of Cardiology and the North American
Society of Pacing and Electrophysiology (1996).
Heart rate variability: standards of measurement, physiological
interpretation, and clinical use.
*Circulation*, 93(5), 1043–1065.
https://doi.org/10.1161/01.CIR.93.5.1043

Applied to synthetic ECG evaluation in:
Golany, T., & Radinsky, K. (2019).
PGANs: personalized generative adversarial networks for ECG synthesis
to improve patient-specific deep ECG classification.
*Proceedings of the AAAI Conference on Artificial Intelligence*, 33, 557–564.
https://doi.org/10.1609/aaai.v33i01.3301557

Implementation notes
--------------------
R-peaks are detected per lead using scipy.signal.find_peaks with a
height threshold of mean + 0.5 · std and a minimum inter-peak distance
corresponding to 40 BPM (1.5 s).  A pure-NumPy fallback (sliding
maximum) is used when scipy is unavailable.

HRV statistics computed per recording:
  SDNN   = standard deviation of RR intervals (ms)
  rMSSD  = root mean square of successive RR differences (ms)
  pNN50  = fraction of successive differences > 50 ms

The score is the Jensen-Shannon divergence between SDNN distributions
of real and synthetic ECGs (lower = more similar HRV).  RMSD of rMSSD
and pNN50 distributions are included in the ``extra`` dict.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import numpy as np

from ecgen_eval.metrics.base import BaseMetric, MetricResult


_REFERENCE = (
    "Task Force of the European Society of Cardiology and the North American Society of Pacing "
    "and Electrophysiology (1996). Heart rate variability: standards of measurement, "
    "physiological interpretation, and clinical use. Circulation, 93(5), 1043–1065. "
    "https://doi.org/10.1161/01.CIR.93.5.1043"
)

_DESCRIPTION = (
    "Heart Rate Variability (HRV): compares SDNN, rMSSD, and pNN50 distributions between "
    "real and synthetic ECGs via Jensen-Shannon divergence. Lower is better."
)


class HRVMetric(BaseMetric):
    """
    HRV statistics comparison per lead.

    Parameters
    ----------
    fs : float
        Sampling frequency in Hz. Default: 500.
    n_subsample : int
        Max samples per lead. Default: 1000.
    seed : int
        Random seed. Default: 42.
    """

    name = "hrv"
    description = _DESCRIPTION
    reference = _REFERENCE
    higher_is_better = False

    def __init__(self, fs: float = 500.0, n_subsample: int = 1000, seed: int = 42):
        self.fs = fs
        self.n_subsample = n_subsample
        self.seed = seed

    def compute(
        self,
        real: np.ndarray,
        synth: np.ndarray,
        lead_names: Optional[List[str]] = None,
    ) -> MetricResult:
        self._check_inputs(real, synth)
        n_leads = real.shape[1]
        if lead_names is None:
            lead_names = [f"L{i+1}" for i in range(n_leads)]

        rng = np.random.default_rng(self.seed)
        per_lead: dict = {}
        extra_detail: dict = {}

        for li, lname in enumerate(lead_names):
            real_l = real[:, li, :]    # (Nr, T)
            synth_l = synth[:, li, :]  # (Ns, T)

            real_l = self._subsample(real_l, rng)
            synth_l = self._subsample(synth_l, rng)

            sdnn_r, rmssd_r, pnn50_r = self._batch_hrv(real_l)
            sdnn_s, rmssd_s, pnn50_s = self._batch_hrv(synth_l)

            js_sdnn = self._js_divergence(sdnn_r, sdnn_s)
            js_rmssd = self._js_divergence(rmssd_r, rmssd_s)
            js_pnn50 = self._js_divergence(pnn50_r, pnn50_s)

            lead_score = float(np.mean([js_sdnn, js_rmssd, js_pnn50]))
            per_lead[lname] = lead_score
            def _safe_nanmean(arr: np.ndarray) -> float:
                valid = arr[~np.isnan(arr)]
                return float(np.mean(valid)) if len(valid) > 0 else float("nan")

            extra_detail[lname] = {
                "real_sdnn_mean": _safe_nanmean(sdnn_r),
                "synth_sdnn_mean": _safe_nanmean(sdnn_s),
                "real_rmssd_mean": _safe_nanmean(rmssd_r),
                "synth_rmssd_mean": _safe_nanmean(rmssd_s),
                "real_pnn50_mean": _safe_nanmean(pnn50_r),
                "synth_pnn50_mean": _safe_nanmean(pnn50_s),
            }

        score = float(np.mean(list(per_lead.values())))
        return MetricResult(
            metric_name=self.name,
            score=score,
            higher_is_better=self.higher_is_better,
            per_lead_scores=per_lead,
            description=self.description,
            reference=self.reference,
            extra=extra_detail,
        )

    # ------------------------------------------------------------------ #
    # HRV helpers                                                          #
    # ------------------------------------------------------------------ #

    def _batch_hrv(
        self, signals: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Compute per-recording HRV stats. Returns arrays of length N."""
        sdnn_vals, rmssd_vals, pnn50_vals = [], [], []
        for sig in signals:
            rr = self._rr_intervals_ms(sig)
            if len(rr) < 2:
                sdnn_vals.append(np.nan)
                rmssd_vals.append(np.nan)
                pnn50_vals.append(np.nan)
            else:
                sdnn_vals.append(float(np.std(rr, ddof=1)))
                diff = np.diff(rr)
                rmssd_vals.append(float(np.sqrt(np.mean(diff ** 2))))
                pnn50_vals.append(float(np.mean(np.abs(diff) > 50.0)))

        return (
            np.array(sdnn_vals, dtype=np.float32),
            np.array(rmssd_vals, dtype=np.float32),
            np.array(pnn50_vals, dtype=np.float32),
        )

    def _rr_intervals_ms(self, signal: np.ndarray) -> np.ndarray:
        """Detect R-peaks and return RR intervals in ms."""
        peaks = self._detect_peaks(signal)
        if len(peaks) < 2:
            return np.array([], dtype=np.float32)
        rr_samples = np.diff(peaks)
        return (rr_samples / self.fs * 1000.0).astype(np.float32)

    def _detect_peaks(self, signal: np.ndarray) -> np.ndarray:
        """R-peak detection; uses scipy if available, else sliding max."""
        min_dist = max(1, int(self.fs * 0.5))  # 40 BPM max → 0.5 s gap
        height = np.mean(signal) + 0.5 * np.std(signal)

        try:
            from scipy.signal import find_peaks
            peaks, _ = find_peaks(signal, height=height, distance=min_dist)
            return peaks
        except ImportError:
            pass

        # Pure-NumPy fallback: sliding maximum
        pad = min_dist // 2
        peaks = []
        for i in range(pad, len(signal) - pad):
            window = signal[max(0, i - pad): i + pad + 1]
            if signal[i] == window.max() and signal[i] >= height:
                if not peaks or (i - peaks[-1]) >= min_dist:
                    peaks.append(i)
        return np.array(peaks, dtype=np.intp)

    # ------------------------------------------------------------------ #
    # Statistics                                                           #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _js_divergence(p_vals: np.ndarray, q_vals: np.ndarray, n_bins: int = 50) -> float:
        """JS divergence between two scalar distributions via histogram binning."""
        p_vals = p_vals[~np.isnan(p_vals)]
        q_vals = q_vals[~np.isnan(q_vals)]
        if len(p_vals) == 0 or len(q_vals) == 0:
            return 0.0

        lo = min(p_vals.min(), q_vals.min())
        hi = max(p_vals.max(), q_vals.max())
        if hi <= lo:
            return 0.0

        bins = np.linspace(lo, hi, n_bins + 1)
        p_hist, _ = np.histogram(p_vals, bins=bins, density=True)
        q_hist, _ = np.histogram(q_vals, bins=bins, density=True)

        p_hist = p_hist + 1e-10
        q_hist = q_hist + 1e-10
        p_hist /= p_hist.sum()
        q_hist /= q_hist.sum()

        m = 0.5 * (p_hist + q_hist)
        eps = 1e-15
        js = 0.5 * (
            np.sum(p_hist * np.log((p_hist + eps) / (m + eps)))
            + np.sum(q_hist * np.log((q_hist + eps) / (m + eps)))
        )
        return float(np.clip(js, 0.0, np.log(2)))

    def _subsample(self, X: np.ndarray, rng: np.random.Generator) -> np.ndarray:
        if X.shape[0] <= self.n_subsample:
            return X
        idx = rng.choice(X.shape[0], size=self.n_subsample, replace=False)
        return X[idx]
