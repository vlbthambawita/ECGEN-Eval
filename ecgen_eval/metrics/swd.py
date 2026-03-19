"""
Sliced Wasserstein Distance (SWD) for ECG distribution comparison.

Reference
---------
Rabin, J., Peyré, G., Delon, J., & Bernot, M. (2011).
Wasserstein barycenter and its application to texture mixing.
*Lecture Notes in Computer Science*, 6667, 435–446.
https://doi.org/10.1007/978-3-642-24785-9_37

Kolouri, S., Nadjahi, K., Simsekli, U., Badeau, R., & Rohde, G. (2019).
Generalized sliced Wasserstein distances.
*Advances in Neural Information Processing Systems (NeurIPS)*, 32.
https://proceedings.neurips.cc/paper/2019/hash/f0935e4cd5920aa6c7c996a5ee53a70f-Abstract.html

Implementation notes
--------------------
We project per-lead feature vectors (same 7 features as MMD) onto
``n_projections`` random unit directions, then compute the exact 1-D
Wasserstein distance (W₁) on each projection via sorted quantile matching.
The final score is the mean over projections and leads.

W₁ on a 1-D projection:  E[|sort(proj_r) - sort(proj_s)|]
  (after interpolating to the same number of quantiles)

Lower SWD means the synthetic distribution is closer to the real one.
"""

from __future__ import annotations

from typing import List, Optional

import numpy as np

from ecgen_eval.metrics.base import BaseMetric, MetricResult


_REFERENCE = (
    "Kolouri, S., Nadjahi, K., Simsekli, U., Badeau, R., & Rohde, G. (2019). "
    "Generalized sliced Wasserstein distances. "
    "Advances in Neural Information Processing Systems (NeurIPS), 32. "
    "https://proceedings.neurips.cc/paper/2019/hash/f0935e4cd5920aa6c7c996a5ee53a70f-Abstract.html"
)

_DESCRIPTION = (
    "Sliced Wasserstein Distance (SWD): approximates the Wasserstein distance between "
    "real and synthetic ECG feature distributions by averaging 1-D projections. "
    "Lower is better (0 = identical distributions)."
)


class SWDMetric(BaseMetric):
    """
    SWD on a 7-dimensional statistical feature space, averaged per lead.

    Parameters
    ----------
    n_projections : int
        Number of random 1-D projections. Default: 200.
    n_subsample : int
        Max samples per lead. Default: 1000.
    seed : int
        Random seed. Default: 42.
    """

    name = "swd"
    description = _DESCRIPTION
    reference = _REFERENCE
    higher_is_better = False

    def __init__(
        self,
        n_projections: int = 200,
        n_subsample: int = 1000,
        seed: int = 42,
    ):
        self.n_projections = n_projections
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

        for li, lname in enumerate(lead_names):
            feats_r = self._extract_features(real[:, li, :])    # (Nr, F)
            feats_s = self._extract_features(synth[:, li, :])   # (Ns, F)

            feats_r = self._subsample(feats_r, rng)
            feats_s = self._subsample(feats_s, rng)

            # Normalise feature space to unit variance
            std = feats_r.std(axis=0) + 1e-9
            feats_r = feats_r / std
            feats_s = feats_s / std

            swd = self._sliced_wasserstein(feats_r, feats_s, rng)
            per_lead[lname] = float(swd)

        score = float(np.mean(list(per_lead.values())))
        return MetricResult(
            metric_name=self.name,
            score=score,
            higher_is_better=self.higher_is_better,
            per_lead_scores=per_lead,
            description=self.description,
            reference=self.reference,
        )

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _sliced_wasserstein(
        self,
        X: np.ndarray,
        Y: np.ndarray,
        rng: np.random.Generator,
    ) -> float:
        """Mean 1-D Wasserstein distance over random projections."""
        n_feats = X.shape[1]
        # Random unit vectors on the sphere
        directions = rng.standard_normal((self.n_projections, n_feats))
        directions /= np.linalg.norm(directions, axis=1, keepdims=True) + 1e-15

        w1_vals = []
        for d in directions:
            proj_r = X @ d  # (Nr,)
            proj_s = Y @ d  # (Ns,)
            w1_vals.append(self._wasserstein1d(proj_r, proj_s))

        return float(np.mean(w1_vals))

    @staticmethod
    def _wasserstein1d(p: np.ndarray, q: np.ndarray) -> float:
        """Exact W₁ via sorted quantile comparison."""
        n = max(len(p), len(q))
        quantiles = np.linspace(0, 1, n)
        p_q = np.quantile(p, quantiles)
        q_q = np.quantile(q, quantiles)
        return float(np.mean(np.abs(p_q - q_q)))

    @staticmethod
    def _extract_features(signals: np.ndarray) -> np.ndarray:
        """7-feature statistical vector per recording (N, T) → (N, 7)."""
        mean_amp = np.mean(signals, axis=1)
        std_amp = np.std(signals, axis=1)
        rms = np.sqrt(np.mean(signals ** 2, axis=1))
        max_abs = np.max(np.abs(signals), axis=1)
        energy = np.sum(signals ** 2, axis=1) / signals.shape[1]
        signs = np.sign(signals)
        zcr = np.sum(np.abs(np.diff(signs, axis=1)), axis=1) / (2.0 * (signals.shape[1] - 1))
        mu = mean_amp[:, None]
        centered = signals - mu
        ac = np.sum(centered[:, :-1] * centered[:, 1:], axis=1) / (
            np.sum(centered ** 2, axis=1) + 1e-9
        )
        return np.stack([mean_amp, std_amp, rms, max_abs, energy, zcr, ac], axis=1).astype(
            np.float32
        )

    def _subsample(self, X: np.ndarray, rng: np.random.Generator) -> np.ndarray:
        if X.shape[0] <= self.n_subsample:
            return X
        idx = rng.choice(X.shape[0], size=self.n_subsample, replace=False)
        return X[idx]
