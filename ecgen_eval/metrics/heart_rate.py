"""
Heart Rate Distribution Comparison for ECG evaluation.

Reference
---------
Pan, J., & Tompkins, W. J. (1985).
A real-time QRS detection algorithm.
*IEEE Transactions on Biomedical Engineering*, 32(3), 230–236.
https://doi.org/10.1109/TBME.1985.325532

Applied to synthetic ECG evaluation in:
Golany, T., & Radinsky, K. (2019).
PGANs: personalized generative adversarial networks for ECG synthesis
to improve patient-specific deep ECG classification.
*Proceedings of the AAAI Conference on Artificial Intelligence*, 33, 557–564.
https://doi.org/10.1609/aaai.v33i01.3301557

Implementation notes
--------------------
R-peaks are detected with the same slope-energy QRS detector as the
HRVMetric (``_rpeaks.py``; up to 300 BPM).  Heart rate is derived as:

  HR (BPM) = 60 / mean(RR_intervals_in_seconds)

The Jensen-Shannon (JS) divergence between the heart-rate distributions of
real and synthetic ECGs is reported as the score (lower = more similar).
Mean and standard deviation of heart rate for both datasets are stored in
``extra``.
"""

from __future__ import annotations

from typing import List, Optional

import numpy as np

from ecgen_eval.metrics._rpeaks import detect_r_peaks
from ecgen_eval.metrics.base import BaseMetric, MetricResult


_REFERENCE = (
    "Pan, J., & Tompkins, W. J. (1985). A real-time QRS detection algorithm. "
    "IEEE Transactions on Biomedical Engineering, 32(3), 230–236. "
    "https://doi.org/10.1109/TBME.1985.325532"
)

_DESCRIPTION = (
    "Heart Rate Distribution: Jensen-Shannon divergence between real and synthetic heart-rate "
    "(BPM) distributions derived from R-peak detection. Lower is better."
)


class HeartRateMetric(BaseMetric):
    """
    Heart-rate distribution comparison per lead.

    Parameters
    ----------
    fs : float
        Sampling frequency in Hz. Default: 500.
    n_subsample : int
        Max samples per lead. Default: 1000.
    seed : int
        Random seed. Default: 42.
    """

    name = "heart_rate"
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
        extra: dict = {}

        for li, lname in enumerate(lead_names):
            real_l = real[:, li, :]    # (Nr, T)
            synth_l = synth[:, li, :]  # (Ns, T)

            real_l = self._subsample(real_l, rng)
            synth_l = self._subsample(synth_l, rng)

            hr_r = self._batch_heart_rate(real_l)    # (Nr,) BPM
            hr_s = self._batch_heart_rate(synth_l)   # (Ns,) BPM

            hr_r = hr_r[~np.isnan(hr_r)]
            hr_s = hr_s[~np.isnan(hr_s)]

            js = self._js_divergence(hr_r, hr_s) if len(hr_r) > 0 and len(hr_s) > 0 else 0.0
            per_lead[lname] = float(js)
            extra[lname] = {
                "real_hr_mean": float(np.mean(hr_r)) if len(hr_r) else float("nan"),
                "real_hr_std": float(np.std(hr_r)) if len(hr_r) else float("nan"),
                "synth_hr_mean": float(np.mean(hr_s)) if len(hr_s) else float("nan"),
                "synth_hr_std": float(np.std(hr_s)) if len(hr_s) else float("nan"),
            }

        score = float(np.mean(list(per_lead.values())))
        return MetricResult(
            metric_name=self.name,
            score=score,
            higher_is_better=self.higher_is_better,
            per_lead_scores=per_lead,
            description=self.description,
            reference=self.reference,
            extra=extra,
        )

    # ------------------------------------------------------------------ #
    # Heart-rate helpers                                                   #
    # ------------------------------------------------------------------ #

    def _batch_heart_rate(self, signals: np.ndarray) -> np.ndarray:
        """Return heart rate (BPM) per recording; NaN when detection fails."""
        hr = []
        for sig in signals:
            peaks = self._detect_peaks(sig)
            if len(peaks) < 2:
                hr.append(np.nan)
            else:
                rr_s = np.diff(peaks) / self.fs  # seconds
                hr.append(float(60.0 / np.mean(rr_s)))
        return np.array(hr, dtype=np.float32)

    def _detect_peaks(self, signal: np.ndarray) -> np.ndarray:
        """R-peak indices (slope-energy QRS detector, see ``_rpeaks.py``)."""
        return detect_r_peaks(signal, self.fs)

    @staticmethod
    def _js_divergence(p_vals: np.ndarray, q_vals: np.ndarray, n_bins: int = 50) -> float:
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
