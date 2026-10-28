"""
Mean Absolute Error (MAE) and Root Mean Square Error (RMSE) for ECG evaluation.

Reference
---------
Standard signal-quality metrics widely used in ECG compression and synthesis:

Zigel, Y., Cohen, A., & Katz, A. (2000).
The weighted diagnostic distortion (WDD) measure for ECG signal compression.
*IEEE Transactions on Biomedical Engineering*, 47(11), 1422–1430.
https://doi.org/10.1109/TBME.2000.880093

Thambawita, V., et al. (2021).
DeepFake electrocardiograms using generative adversarial networks are the
beginning of the end for privacy issues in medicine.
*Scientific Reports*, 11, 21896.
https://doi.org/10.1038/s41598-021-01295-2

Implementation notes
--------------------
For each real ECG recording we find its nearest synthetic neighbour
(minimum MSE across flattened lead signals) and compute:

  MAE  = (1/T) · Σ |real[t] − synth_nn[t]|
  RMSE = sqrt((1/T) · Σ (real[t] − synth_nn[t])²)

Both are computed per lead and averaged.  The primary score is MAE;
RMSE is included in the ``extra`` dict.
"""

from __future__ import annotations

from typing import List, Optional

import numpy as np

from ecgen_eval.metrics.base import BaseMetric, MetricResult


_REFERENCE = (
    "Zigel, Y., Cohen, A., & Katz, A. (2000). The weighted diagnostic distortion (WDD) measure "
    "for ECG signal compression. IEEE Transactions on Biomedical Engineering, 47(11), 1422–1430. "
    "https://doi.org/10.1109/TBME.2000.880093"
)

_DESCRIPTION = (
    "Mean Absolute Error (MAE): average pointwise deviation between real ECGs and their nearest "
    "synthetic neighbours, computed per lead. Lower is better (0 = perfect reconstruction)."
)


class MAEMetric(BaseMetric):
    """
    Nearest-neighbour MAE and RMSE per lead.

    Parameters
    ----------
    n_subsample : int
        Max samples per lead for speed. Default: 500.
    seed : int
        Random seed. Default: 42.
    """

    name = "mae"
    description = _DESCRIPTION
    reference = _REFERENCE
    higher_is_better = False

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
        per_lead_mae: dict = {}
        per_lead_rmse: dict = {}

        for li, lname in enumerate(lead_names):
            real_l = real[:, li, :]    # (Nr, T)
            synth_l = synth[:, li, :]  # (Ns, T)

            real_l = self._subsample(real_l, rng)
            synth_l = self._subsample(synth_l, rng)

            mae_vals = []
            rmse_vals = []
            for i in range(len(real_l)):
                diff = synth_l - real_l[i]           # (Ns, T)
                mse_vec = np.mean(diff ** 2, axis=1)  # (Ns,)
                nn = np.argmin(mse_vec)
                residual = diff[nn]                   # (T,)
                mae_vals.append(float(np.mean(np.abs(residual))))
                rmse_vals.append(float(np.sqrt(mse_vec[nn])))

            per_lead_mae[lname] = float(np.mean(mae_vals))
            per_lead_rmse[lname] = float(np.mean(rmse_vals))

        score = float(np.mean(list(per_lead_mae.values())))
        return MetricResult(
            metric_name=self.name,
            score=score,
            higher_is_better=self.higher_is_better,
            per_lead_scores=per_lead_mae,
            description=self.description,
            reference=self.reference,
            extra={"per_lead_rmse": per_lead_rmse, "rmse": float(np.mean(list(per_lead_rmse.values())))},
        )

    def _subsample(self, X: np.ndarray, rng: np.random.Generator) -> np.ndarray:
        if X.shape[0] <= self.n_subsample:
            return X
        idx = rng.choice(X.shape[0], size=self.n_subsample, replace=False)
        return X[idx]
