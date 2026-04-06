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
        """
        Input : (N, T)
        Output: (N, 11) float64
        """
        x = signals.astype(np.float64)
        T = x.shape[1]

        mean = np.mean(x, axis=1)
        std = np.std(x, axis=1) + 1e-9
        rms = np.sqrt(np.mean(x ** 2, axis=1))
        energy = np.sum(x ** 2, axis=1) / T
        max_abs = np.max(np.abs(x), axis=1)

        # Skewness and kurtosis (standardised central moments)
        centred = x - mean[:, None]
        skew = np.mean((centred / std[:, None]) ** 3, axis=1)
        kurt = np.mean((centred / std[:, None]) ** 4, axis=1)

        # Zero-crossing rate
        signs = np.sign(x)
        zcr = np.sum(np.abs(np.diff(signs, axis=1)), axis=1) / (2.0 * (T - 1))

        # Lag-1 autocorrelation
        ac = np.sum(centred[:, :-1] * centred[:, 1:], axis=1) / (
            np.sum(centred ** 2, axis=1) + 1e-9
        )

        # Spectral centroid and bandwidth (from magnitude FFT)
        fft_mag = np.abs(np.fft.rfft(x, axis=1))
        freqs = np.arange(fft_mag.shape[1], dtype=np.float64)
        total_power = np.sum(fft_mag, axis=1) + 1e-9
        spectral_centroid = np.sum(fft_mag * freqs[None, :], axis=1) / total_power
        spectral_bandwidth = np.sqrt(
            np.sum(fft_mag * (freqs[None, :] - spectral_centroid[:, None]) ** 2, axis=1)
            / total_power
        )

        feats = np.stack([
            mean, std, rms, energy, max_abs, skew, kurt,
            zcr, ac, spectral_centroid, spectral_bandwidth
        ], axis=1)
        return feats

