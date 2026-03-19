"""
Peak Signal-to-Noise Ratio (PSNR) for ECG evaluation.

Reference
---------
Huynh-Thu, Q., & Ghanbari, M. (2008).
Scope of validity of PSNR in image/video quality assessment.
*Electronics Letters*, 44(13), 800–801.
https://doi.org/10.1049/el:20080522

Applied to ECG synthesis evaluation in:
Thambawita, V., et al. (2021).
DeepFake electrocardiograms using generative adversarial networks are the
beginning of the end for privacy issues in medicine.
*Scientific Reports*, 11, 21896.
https://doi.org/10.1038/s41598-021-01295-2

Implementation notes
--------------------
For each real ECG recording we identify its nearest synthetic neighbour
(minimum MSE in the flattened time-series space per lead), then compute
PSNR using the peak-to-peak amplitude of the real signal as MAX.

PSNR (dB) = 10 · log10(MAX² / MSE)

Higher values indicate better reconstruction quality (higher is better).
"""

from __future__ import annotations

from typing import List, Optional

import numpy as np

from ecgen_eval.metrics.base import BaseMetric, MetricResult


_REFERENCE = (
    "Huynh-Thu, Q., & Ghanbari, M. (2008). Scope of validity of PSNR in image/video quality "
    "assessment. Electronics Letters, 44(13), 800–801. https://doi.org/10.1049/el:20080522"
)

_DESCRIPTION = (
    "Peak Signal-to-Noise Ratio (PSNR): measures waveform reconstruction quality between "
    "real ECGs and their nearest synthetic neighbours. Reported in dB; higher is better."
)


class PSNRMetric(BaseMetric):
    """
    Nearest-neighbour PSNR averaged per lead and across leads.

    Parameters
    ----------
    n_subsample : int
        Maximum samples drawn from each dataset per lead. Default: 500.
    seed : int
        Random seed for subsampling. Default: 42.
    """

    name = "psnr"
    description = _DESCRIPTION
    reference = _REFERENCE
    higher_is_better = True

    def __init__(self, n_subsample: int = 500, seed: int = 42):
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

            psnr_vals = []
            for i in range(len(real_l)):
                mse_vec = np.mean((synth_l - real_l[i]) ** 2, axis=1)  # (Ns,)
                mse = float(mse_vec.min())
                max_val = float(np.ptp(real_l[i]))  # peak-to-peak
                if max_val < 1e-9:
                    psnr_vals.append(100.0)
                elif mse < 1e-15:
                    psnr_vals.append(100.0)
                else:
                    psnr_vals.append(10.0 * np.log10(max_val ** 2 / mse))

            per_lead[lname] = float(np.mean(psnr_vals))

        score = float(np.mean(list(per_lead.values())))
        return MetricResult(
            metric_name=self.name,
            score=score,
            higher_is_better=self.higher_is_better,
            per_lead_scores=per_lead,
            description=self.description,
            reference=self.reference,
        )

    def _subsample(self, X: np.ndarray, rng: np.random.Generator) -> np.ndarray:
        if X.shape[0] <= self.n_subsample:
            return X
        idx = rng.choice(X.shape[0], size=self.n_subsample, replace=False)
        return X[idx]
