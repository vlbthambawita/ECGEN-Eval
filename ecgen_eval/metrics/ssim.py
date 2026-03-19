"""
Structural Similarity Index Measure (SSIM) adapted for 1-D ECG signals.

Reference
---------
Wang, Z., Bovik, A. C., Sheikh, H. R., & Simoncelli, E. P. (2004).
Image quality assessment: from error visibility to structural similarity.
*IEEE Transactions on Image Processing*, 13(4), 600–612.
https://doi.org/10.1109/TIP.2003.819861

Applied to ECG quality assessment in:
Hayn, D., et al. (2018).
Electrocardiogram signal quality assessment based on structural image
similarity metric.
*Physiological Measurement*, 39(1), 014005.
https://doi.org/10.1088/1361-6579/aa9f5b

Implementation notes
--------------------
The standard SSIM formula is applied globally (not windowed) to matched
pairs of 1-D ECG signals:

  SSIM(x, y) = [(2μx·μy + C1)(2σxy + C2)] / [(μx² + μy² + C1)(σx² + σy² + C2)]

where C1 = (k1·L)², C2 = (k2·L)², L = dynamic range of real signal,
k1 = 0.01, k2 = 0.03.

For unpaired evaluation, each real signal is matched to its nearest
synthetic neighbour (minimum MSE) before computing SSIM.  Score range:
[-1, 1], higher is better; 1 = identical.
"""

from __future__ import annotations

from typing import List, Optional

import numpy as np

from ecgen_eval.metrics.base import BaseMetric, MetricResult


_REFERENCE = (
    "Wang, Z., Bovik, A. C., Sheikh, H. R., & Simoncelli, E. P. (2004). "
    "Image quality assessment: from error visibility to structural similarity. "
    "IEEE Transactions on Image Processing, 13(4), 600–612. "
    "https://doi.org/10.1109/TIP.2003.819861"
)

_DESCRIPTION = (
    "Structural Similarity Index (SSIM): measures luminance, contrast, and structural "
    "similarity between real and nearest-synthetic ECG waveforms. Range [-1, 1]; higher is better."
)


class SSIMMetric(BaseMetric):
    """
    Global 1-D SSIM averaged per lead.

    Parameters
    ----------
    k1, k2 : float
        Stability constants. Default: 0.01, 0.03 (standard values).
    n_subsample : int
        Max samples per lead for speed. Default: 500.
    seed : int
        Random seed. Default: 42.
    """

    name = "ssim"
    description = _DESCRIPTION
    reference = _REFERENCE
    higher_is_better = True

    def __init__(
        self,
        k1: float = 0.01,
        k2: float = 0.03,
        n_subsample: int = 500,
        seed: int = 42,
    ):
        self.k1 = k1
        self.k2 = k2
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
            real_l = real[:, li, :]    # (Nr, T)
            synth_l = synth[:, li, :]  # (Ns, T)

            real_l = self._subsample(real_l, rng)
            synth_l = self._subsample(synth_l, rng)

            ssim_vals = []
            for i in range(len(real_l)):
                x = real_l[i]
                # Find nearest synthetic neighbour
                mse_vec = np.mean((synth_l - x) ** 2, axis=1)
                nn = synth_l[np.argmin(mse_vec)]

                ssim_vals.append(self._ssim_1d(x, nn))

            per_lead[lname] = float(np.mean(ssim_vals))

        score = float(np.mean(list(per_lead.values())))
        return MetricResult(
            metric_name=self.name,
            score=score,
            higher_is_better=self.higher_is_better,
            per_lead_scores=per_lead,
            description=self.description,
            reference=self.reference,
        )

    def _ssim_1d(self, x: np.ndarray, y: np.ndarray) -> float:
        """Global SSIM between two 1-D arrays."""
        L = float(np.ptp(x)) if np.ptp(x) > 1e-9 else 1.0
        C1 = (self.k1 * L) ** 2
        C2 = (self.k2 * L) ** 2

        mu_x = float(np.mean(x))
        mu_y = float(np.mean(y))
        sig_x = float(np.var(x))
        sig_y = float(np.var(y))
        sig_xy = float(np.mean((x - mu_x) * (y - mu_y)))

        num = (2 * mu_x * mu_y + C1) * (2 * sig_xy + C2)
        den = (mu_x ** 2 + mu_y ** 2 + C1) * (sig_x + sig_y + C2)
        return float(num / den) if den > 1e-15 else 1.0

    def _subsample(self, X: np.ndarray, rng: np.random.Generator) -> np.ndarray:
        if X.shape[0] <= self.n_subsample:
            return X
        idx = rng.choice(X.shape[0], size=self.n_subsample, replace=False)
        return X[idx]
