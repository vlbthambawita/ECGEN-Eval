"""
Nearest-Neighbour Distance (NND) for ECG memorisation / privacy assessment.

Reference
---------
Meehan, C., Chaudhuri, K., & Dasgupta, S. (2020).
A non-parametric test to detect data-copying in generative models.
*Proceedings of the 23rd International Conference on Artificial
Intelligence and Statistics (AISTATS)*, 119, 3012–3022.
https://proceedings.mlr.press/v119/meehan20a.html

Zhao, S., Liu, Z., Lin, J., Zhu, J.-Y., & Han, S. (2018).
Differentiable augmentation for data-efficient GAN training.
*Advances in Neural Information Processing Systems (NeurIPS)*, 33.

Implementation notes
--------------------
For each real ECG recording we compute:
  - d(real, synth): distance to its nearest synthetic neighbour.
  - d(real, real):  distance to its nearest *other* real neighbour.

The Authenticity score is the fraction of synthetic samples whose
nearest-real-neighbour distance exceeds the real-vs-real baseline
(i.e., synthetic samples that are not near-duplicates of any real sample).

NND score = mean d(real, synth) per lead (lower → synthetic is closer to real).
Authenticity = fraction of synth that are NOT near-copies of real (higher → more diverse).

The primary score is d(real, synth) (lower is better); Authenticity is in extra.
"""

from __future__ import annotations

from typing import List, Optional

import numpy as np

from ecgen_eval.metrics.base import BaseMetric, MetricResult


_REFERENCE = (
    "Meehan, C., Chaudhuri, K., & Dasgupta, S. (2020). "
    "A non-parametric test to detect data-copying in generative models. "
    "Proceedings of AISTATS 2020, 119, 3012–3022. "
    "https://proceedings.mlr.press/v119/meehan20a.html"
)

_DESCRIPTION = (
    "Nearest-Neighbour Distance (NND): mean distance from each real ECG to its nearest "
    "synthetic neighbour in statistical feature space. Lower = synthetic is closer to real. "
    "Authenticity (in extra) = fraction of synthetic not memorising any real sample."
)


class NNDistMetric(BaseMetric):
    """
    NND and Authenticity computed per lead on a 7-feature statistical space.

    Parameters
    ----------
    n_subsample : int
        Max samples per lead. Default: 1000.
    seed : int
        Random seed. Default: 42.
    """

    name = "nn_dist"
    description = _DESCRIPTION
    reference = _REFERENCE
    higher_is_better = False

    def __init__(self, n_subsample: int = 1000, seed: int = 42):
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
        authenticity: dict = {}

        for li, lname in enumerate(lead_names):
            feats_r = self._extract_features(real[:, li, :])    # (Nr, F)
            feats_s = self._extract_features(synth[:, li, :])   # (Ns, F)

            feats_r = self._subsample(feats_r, rng)
            feats_s = self._subsample(feats_s, rng)

            # Normalise
            std = feats_r.std(axis=0) + 1e-9
            feats_r_n = feats_r / std
            feats_s_n = feats_s / std

            # d(real, synth)
            sq_rs = self._pairwise_sq_dist(feats_r_n, feats_s_n)  # (Nr, Ns)
            nnd_rs = float(np.sqrt(sq_rs.min(axis=1)).mean())       # mean over real

            # d(real, real) — to build the baseline threshold
            sq_rr = self._pairwise_sq_dist(feats_r_n, feats_r_n)   # (Nr, Nr)
            np.fill_diagonal(sq_rr, np.inf)
            nnd_rr = np.sqrt(sq_rr.min(axis=1))  # (Nr,) nearest other real

            # Authenticity: fraction of synth farther from real than the typical real-real gap
            threshold = float(np.median(nnd_rr))
            nnd_sr = np.sqrt(sq_rs.min(axis=0))  # (Ns,) nearest real for each synth
            auth = float(np.mean(nnd_sr > threshold))

            per_lead[lname] = nnd_rs
            authenticity[lname] = auth

        score = float(np.mean(list(per_lead.values())))
        return MetricResult(
            metric_name=self.name,
            score=score,
            higher_is_better=self.higher_is_better,
            per_lead_scores=per_lead,
            description=self.description,
            reference=self.reference,
            extra={"authenticity": authenticity},
        )

    @staticmethod
    def _pairwise_sq_dist(A: np.ndarray, B: np.ndarray) -> np.ndarray:
        diff = A[:, None, :] - B[None, :, :]
        return np.sum(diff ** 2, axis=-1)

    @staticmethod
    def _extract_features(signals: np.ndarray) -> np.ndarray:
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
