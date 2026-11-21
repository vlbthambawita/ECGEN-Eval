"""
Fréchet Distance (FD) metric for ECG evaluation.

Computes the Fréchet Distance between the multivariate Gaussian distributions
fitted to feature vectors extracted from real and synthetic ECGs.

This is analogous to the Fréchet Inception Distance (FID) used in image generation,
but uses a handcrafted signal feature extractor instead of a deep-network embedding.

Reference
---------
Heusel, M., Ramsauer, H., Unterthiner, T., Nessler, B., & Hochreiter, S. (2017).
GANs trained by a two time-scale update rule converge to a local Nash equilibrium.
*NeurIPS*, 30. https://arxiv.org/abs/1706.08500

Fréchet, M. (1957). Sur la distance de deux lois de probabilité.
*Publications de l'Institut de Statistique de l'Université de Paris*, 6, 183–198.

ECG application:
  Thambawita, V., et al. (2021). DeepFake electrocardiograms using generative
  adversarial networks are the beginning of the end for privacy issues in medicine.
  *Scientific Reports*, 11, 21896. https://doi.org/10.1038/s41598-021-01295-2

Implementation notes
--------------------
Feature vector (per lead, per recording):
  - Mean, standard deviation, skewness, kurtosis
  - RMS, energy, max absolute amplitude
  - Zero-crossing rate, lag-1 autocorrelation
  - Spectral centroid, spectral bandwidth (from magnitude FFT)

The features are z-score standardised before fitting Gaussians.

FD = ‖μ_r − μ_s‖² + Tr(Σ_r + Σ_s − 2·(Σ_r Σ_s)^½)

Overall score: mean FD across all leads.
"""

from __future__ import annotations

from typing import List, Optional

import numpy as np

from ecgen_eval.metrics._signal_features import extended_features
from ecgen_eval.metrics.base import BaseMetric, MetricResult
from ecgen_eval.metrics._frechet_utils import frechet_distance


_REFERENCE = (
    "Heusel, M., et al. (2017). GANs trained by a two time-scale update rule converge "
    "to a local Nash equilibrium. NeurIPS, 30. https://arxiv.org/abs/1706.08500 | "
    "Thambawita, V., et al. (2021). DeepFake electrocardiograms. Scientific Reports, 11, 21896. "
    "https://doi.org/10.1038/s41598-021-01295-2"
)

_DESCRIPTION = (
    "Fréchet Distance (FD): measures the distance between multivariate Gaussians fitted "
    "to ECG feature embeddings of real and synthetic sets per lead. "
    "Analogous to FID for images. Lower is better."
)

# Number of features extracted per lead per recording
_N_FEATURES = 11


class FDMetric(BaseMetric):
    """
    Fréchet Distance between Gaussian fits to ECG feature vectors per lead.

    Parameters
    ----------
    n_subsample : int
        Maximum samples per set. Default: 2000.
    eps : float
        Small regularisation term added to covariance diagonal for stability.
    """

    name = "fd"
    description = _DESCRIPTION
    reference = _REFERENCE
    higher_is_better = False

    def __init__(self, n_subsample: int = 2000, eps: float = 1e-6):
        self.n_subsample = n_subsample
        self.eps = eps

    # ------------------------------------------------------------------ #

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

        rng = np.random.default_rng(42)
        r = real if real.shape[0] <= self.n_subsample else real[
            rng.choice(real.shape[0], self.n_subsample, replace=False)]
        s = synth if synth.shape[0] <= self.n_subsample else synth[
            rng.choice(synth.shape[0], self.n_subsample, replace=False)]

        per_lead: dict = {}

        for li, lname in enumerate(lead_names):
            feats_r = self._extract_features(r[:, li, :])
            feats_s = self._extract_features(s[:, li, :])

            # Z-score normalise using real statistics
            mu_norm = feats_r.mean(axis=0)
            std_norm = feats_r.std(axis=0) + 1e-9
            feats_r = (feats_r - mu_norm) / std_norm
            feats_s = (feats_s - mu_norm) / std_norm

            fd = frechet_distance(feats_r, feats_s, eps=self.eps)
            per_lead[lname] = float(fd)

        overall = float(np.mean(list(per_lead.values())))

        return MetricResult(
            metric_name=self.name,
            score=overall,
            higher_is_better=self.higher_is_better,
            per_lead_scores=per_lead,
            description=self.description,
            reference=self.reference,
        )

    # ------------------------------------------------------------------ #
    # Feature extraction                                                   #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _extract_features(signals: np.ndarray) -> np.ndarray:
        """11-feature vector per recording (N, T) → (N, 11) float64."""
        return extended_features(signals)
