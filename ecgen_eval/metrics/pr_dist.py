"""
Precision and Recall for generative model distributions (ECG adaptation).

Reference
---------
Kynkäänniemi, T., Karras, T., Laine, S., Lehtinen, J., & Aila, T. (2019).
Improved Precision and Recall Metric for Assessing Generative Models.
*Advances in Neural Information Processing Systems (NeurIPS)*, 32.
https://proceedings.neurips.cc/paper/2019/hash/0234c510bc6d908b28c70ff313743079-Abstract.html

Implementation notes
--------------------
For each lead, we extract the same 7 statistical features used by the MMD
metric, then estimate the real and synthetic data manifolds using k-NN.

Precision: fraction of synthetic samples whose nearest-real-neighbour
  distance is ≤ the k-th nearest-neighbour distance within the real set.
  (i.e., synthetic point falls "inside" the real manifold support.)

Recall: fraction of real samples whose nearest-synthetic-neighbour
  distance is ≤ the k-th nearest-neighbour distance within the synthetic set.

Both range [0, 1]; higher is better.  The primary scalar score is the
harmonic mean (F-score) of Precision and Recall.
"""

from __future__ import annotations

from typing import List, Optional

import numpy as np

from ecgen_eval.metrics.base import BaseMetric, MetricResult


_REFERENCE = (
    "Kynkäänniemi, T., Karras, T., Laine, S., Lehtinen, J., & Aila, T. (2019). "
    "Improved Precision and Recall Metric for Assessing Generative Models. "
    "Advances in Neural Information Processing Systems (NeurIPS), 32. "
    "https://proceedings.neurips.cc/paper/2019/hash/0234c510bc6d908b28c70ff313743079-Abstract.html"
)

_DESCRIPTION = (
    "Distribution Precision & Recall: estimates fidelity (Precision) and diversity (Recall) "
    "of synthetic ECG distributions relative to real ECG distributions via k-NN manifold "
    "estimation. Score = F1 of Precision and Recall. Higher is better."
)


class PRDistMetric(BaseMetric):
    """
    Precision/Recall for distributions, per lead.

    Parameters
    ----------
    k : int
        k for k-NN manifold estimation. Default: 3.
    n_subsample : int
        Max samples per lead. Default: 1000.
    seed : int
        Random seed. Default: 42.
    """

    name = "pr_dist"
    description = _DESCRIPTION
    reference = _REFERENCE
    higher_is_better = True

    def __init__(self, k: int = 3, n_subsample: int = 1000, seed: int = 42):
        self.k = k
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
        precision_vals: dict = {}
        recall_vals: dict = {}

        for li, lname in enumerate(lead_names):
            feats_r = self._extract_features(real[:, li, :])    # (Nr, F)
            feats_s = self._extract_features(synth[:, li, :])   # (Ns, F)

            feats_r = self._subsample(feats_r, rng)
            feats_s = self._subsample(feats_s, rng)

            # Normalise
            std = feats_r.std(axis=0) + 1e-9
            feats_r = feats_r / std
            feats_s = feats_s / std

            prec = self._precision(feats_r, feats_s)
            rec = self._recall(feats_r, feats_s)

            precision_vals[lname] = float(prec)
            recall_vals[lname] = float(rec)
            f1 = 2 * prec * rec / (prec + rec + 1e-9)
            per_lead[lname] = float(f1)

        score = float(np.mean(list(per_lead.values())))
        return MetricResult(
            metric_name=self.name,
            score=score,
            higher_is_better=self.higher_is_better,
            per_lead_scores=per_lead,
            description=self.description,
            reference=self.reference,
            extra={"precision": precision_vals, "recall": recall_vals},
        )

    # ------------------------------------------------------------------ #
    # Precision / Recall                                                   #
    # ------------------------------------------------------------------ #

    def _knn_radii(self, X: np.ndarray) -> np.ndarray:
        """k-th nearest-neighbour distance within X for each point in X."""
        k = min(self.k, X.shape[0] - 1)
        sq_dist = self._pairwise_sq_dist(X, X)  # (N, N)
        np.fill_diagonal(sq_dist, np.inf)
        # Sort and take k-th smallest
        sorted_dists = np.sort(sq_dist, axis=1)  # ascending
        return np.sqrt(sorted_dists[:, k - 1])   # (N,)

    def _precision(self, real_feats: np.ndarray, synth_feats: np.ndarray) -> float:
        """Fraction of synth in real manifold."""
        radii_r = self._knn_radii(real_feats)  # (Nr,)
        # For each synth, distance to nearest real
        sq = self._pairwise_sq_dist(synth_feats, real_feats)  # (Ns, Nr)
        nn_dist = np.sqrt(sq.min(axis=1))  # (Ns,)
        nn_idx = sq.argmin(axis=1)         # nearest real for each synth
        return float(np.mean(nn_dist <= radii_r[nn_idx]))

    def _recall(self, real_feats: np.ndarray, synth_feats: np.ndarray) -> float:
        """Fraction of real in synth manifold."""
        radii_s = self._knn_radii(synth_feats)  # (Ns,)
        sq = self._pairwise_sq_dist(real_feats, synth_feats)  # (Nr, Ns)
        nn_dist = np.sqrt(sq.min(axis=1))
        nn_idx = sq.argmin(axis=1)
        return float(np.mean(nn_dist <= radii_s[nn_idx]))

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
