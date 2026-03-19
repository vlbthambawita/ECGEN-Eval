"""
Maximum Mean Discrepancy (MMD) metric for ECG evaluation.

Reference
---------
Gretton, A., Borgwardt, K. M., Rasch, M. J., Schölkopf, B., & Smola, A. (2012).
A kernel two-sample test.
*Journal of Machine Learning Research*, 13, 723–773.
https://jmlr.org/papers/v13/gretton12a.html

Implementation notes
--------------------
We compute MMD² with a mixture of RBF kernels (multi-scale) on per-lead
feature vectors extracted from each ECG recording.

Features used per lead (to keep MMD in a meaningful signal space):
  - Mean amplitude
  - Standard deviation of amplitude
  - Root Mean Square (RMS)
  - Maximum absolute amplitude
  - Signal energy (sum of squares / T)
  - Zero-crossing rate
  - First-order autocorrelation

These statistics capture both amplitude distribution and temporal structure
without requiring R-peak detection (no preprocessing dependency).

The multi-scale RBF kernel uses bandwidths [0.1, 1.0, 10.0] * median heuristic,
following the recommendation in Gretton et al. (2012).
"""

from __future__ import annotations

from typing import List, Optional

import numpy as np

from ecgen_eval.metrics.base import BaseMetric, MetricResult


_REFERENCE = (
    "Gretton, A., Borgwardt, K. M., Rasch, M. J., Schölkopf, B., & Smola, A. (2012). "
    "A kernel two-sample test. Journal of Machine Learning Research, 13, 723–773. "
    "https://jmlr.org/papers/v13/gretton12a.html"
)

_DESCRIPTION = (
    "Maximum Mean Discrepancy (MMD): measures the distance between the distributions "
    "of real and synthetic ECGs in a reproducing kernel Hilbert space. "
    "Score of 0 means identical distributions. Lower is better."
)


class MMDMetric(BaseMetric):
    """
    MMD² computed per lead on a handcrafted statistical feature vector,
    then averaged across leads to yield a single scalar score.

    Parameters
    ----------
    kernel_bandwidths : list of float, optional
        Multiplicative factors applied to the median-heuristic bandwidth.
        Default: [0.1, 1.0, 10.0] (multi-scale RBF).
    n_subsample : int, optional
        Maximum number of samples drawn from each dataset per lead before
        computing the kernel matrix (for speed). Default: 1000.
    """

    name = "mmd"
    description = _DESCRIPTION
    reference = _REFERENCE
    higher_is_better = False

    def __init__(
        self,
        kernel_bandwidths: Optional[List[float]] = None,
        n_subsample: int = 1000,
    ):
        self.kernel_bandwidths = kernel_bandwidths or [0.1, 1.0, 10.0]
        self.n_subsample = n_subsample

    # ------------------------------------------------------------------ #
    # Public                                                               #
    # ------------------------------------------------------------------ #

    def compute(
        self,
        real: np.ndarray,
        synth: np.ndarray,
        lead_names: Optional[List[str]] = None,
    ) -> MetricResult:
        """
        Parameters
        ----------
        real  : (N_r, L, T)
        synth : (N_s, L, T)
        """
        self._check_inputs(real, synth)
        n_leads = real.shape[1]
        if lead_names is None:
            lead_names = [f"L{i+1}" for i in range(n_leads)]

        per_lead: dict = {}
        for li, lname in enumerate(lead_names):
            feats_r = self._extract_features(real[:, li, :])   # (N_r, F)
            feats_s = self._extract_features(synth[:, li, :])  # (N_s, F)

            # Subsample for speed
            feats_r = self._subsample(feats_r)
            feats_s = self._subsample(feats_s)

            mmd2 = self._mmd_squared(feats_r, feats_s)
            per_lead[lname] = float(np.maximum(mmd2, 0.0))  # clip small negatives

        overall = float(np.mean(list(per_lead.values())))

        return MetricResult(
            metric_name=self.name,
            score=overall,
            higher_is_better=self.higher_is_better,
            per_lead_scores=per_lead,
            description=self.description,
            reference=self.reference,
            extra={"per_lead_mmd2": per_lead},
        )

    # ------------------------------------------------------------------ #
    # Feature extraction                                                   #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _extract_features(signals: np.ndarray) -> np.ndarray:
        """
        Extract a statistical feature vector per recording.

        Input : (N, T)
        Output: (N, 7) float32
        """
        mean_amp = np.mean(signals, axis=1)
        std_amp = np.std(signals, axis=1)
        rms = np.sqrt(np.mean(signals ** 2, axis=1))
        max_abs = np.max(np.abs(signals), axis=1)
        energy = np.sum(signals ** 2, axis=1) / signals.shape[1]
        # Zero-crossing rate
        signs = np.sign(signals)
        zcr = np.sum(np.abs(np.diff(signs, axis=1)), axis=1) / (2.0 * (signals.shape[1] - 1))
        # Lag-1 autocorrelation
        mu = mean_amp[:, None]
        centered = signals - mu
        ac = np.sum(centered[:, :-1] * centered[:, 1:], axis=1) / (
            np.sum(centered ** 2, axis=1) + 1e-9
        )

        feats = np.stack([mean_amp, std_amp, rms, max_abs, energy, zcr, ac], axis=1)
        return feats.astype(np.float32)

    # ------------------------------------------------------------------ #
    # Kernel & MMD                                                         #
    # ------------------------------------------------------------------ #

    def _mmd_squared(self, X: np.ndarray, Y: np.ndarray) -> float:
        """
        Biased MMD² estimator with multi-scale RBF kernel.
        MMD²(X,Y) = E[k(x,x')] - 2·E[k(x,y)] + E[k(y,y')]
        """
        XX = self._kernel_matrix(X, X)
        YY = self._kernel_matrix(Y, Y)
        XY = self._kernel_matrix(X, Y)

        n = X.shape[0]
        m = Y.shape[0]

        # Unbiased estimator: zero diagonal on same-set terms
        np.fill_diagonal(XX, 0.0)
        np.fill_diagonal(YY, 0.0)

        mmd2 = (
            XX.sum() / (n * (n - 1))
            + YY.sum() / (m * (m - 1))
            - 2.0 * XY.mean()
        )
        return float(mmd2)

    def _kernel_matrix(self, A: np.ndarray, B: np.ndarray) -> np.ndarray:
        """Sum of RBF kernels with multiple bandwidths."""
        # Squared Euclidean distances
        diff = A[:, None, :] - B[None, :, :]         # (N, M, F)
        sq_dist = np.sum(diff ** 2, axis=-1)          # (N, M)

        # Median heuristic bandwidth
        sigma2 = np.median(sq_dist) + 1e-9

        K = np.zeros_like(sq_dist)
        for bw in self.kernel_bandwidths:
            K += np.exp(-sq_dist / (2.0 * bw * sigma2))
        return K / len(self.kernel_bandwidths)

    def _subsample(self, X: np.ndarray) -> np.ndarray:
        if X.shape[0] <= self.n_subsample:
            return X
        rng = np.random.default_rng(42)
        idx = rng.choice(X.shape[0], size=self.n_subsample, replace=False)
        return X[idx]
