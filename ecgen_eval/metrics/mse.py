"""
Mean Squared Error (MSE) and Root Mean Square Error (RMSE) for ECG evaluation.

Reference
---------
Wang, Z., & Bovik, A. C. (2009).
Mean squared error: Love it or leave it? A new look at signal fidelity measures.
*IEEE Signal Processing Magazine*, 26(1), 98–117.
https://doi.org/10.1109/MSP.2008.930649

Zigel, Y., Cohen, A., & Katz, A. (2000).
The weighted diagnostic distortion (WDD) measure for ECG signal compression.
*IEEE Transactions on Biomedical Engineering*, 47(11), 1422–1430.
https://doi.org/10.1109/TBME.2000.880093

Implementation notes
--------------------
Per lead, real and synthetic signals are matched according to ``pairing``
(see :mod:`ecgen_eval.metrics._matching`) and for every pair

  MSE  = (1/T) · Σ (real[t] − synth[t])²
  RMSE = sqrt(MSE)

The lead score is the mean over pairs (RMSE is the mean of per-pair RMSE, not the
root of the mean MSE). With default settings ``RMSEMetric`` equals the ``rmse``
value that :class:`~ecgen_eval.metrics.mae.MAEMetric` reports in ``extra``.
"""

from __future__ import annotations

from typing import Dict, Optional

import numpy as np

from ecgen_eval.metrics._pairwise import PairwiseSignalMetric

_REFERENCE = (
    "Wang, Z., & Bovik, A. C. (2009). Mean squared error: Love it or leave it? A new look at "
    "signal fidelity measures. IEEE Signal Processing Magazine, 26(1), 98–117. "
    "https://doi.org/10.1109/MSP.2008.930649"
)

_MSE_DESCRIPTION = (
    "Mean Squared Error (MSE): average squared pointwise deviation between real ECGs and their "
    "matched synthetic ECGs, computed per lead. Lower is better (0 = identical)."
)

_RMSE_DESCRIPTION = (
    "Root Mean Square Error (RMSE): square root of the pointwise MSE between real ECGs and their "
    "matched synthetic ECGs, in signal units, computed per lead. Lower is better (0 = identical)."
)


def pair_mse(R: np.ndarray, S: np.ndarray) -> np.ndarray:
    """Per-pair mean squared error. ``(M, T), (M, T) -> (M,)``."""
    diff = np.asarray(R, dtype=np.float64) - np.asarray(S, dtype=np.float64)
    return np.mean(diff ** 2, axis=1)


class MSEMetric(PairwiseSignalMetric):
    """
    Mean squared error between matched real and synthetic signals, per lead.

    Parameters
    ----------
    pairing : {'nn', 'paired', 'mean'}
        How real and synthetic signals are matched. Default: 'nn' (each real signal
        against its nearest synthetic signal of the same lead).
    n_subsample : int
        Max recordings per set. Default: 500.
    normalize : {None, 'zscore', 'minmax'}
        Per-recording, per-lead normalisation applied before matching. Default: None
        (signal units).
    baseline : bool
        Also score two disjoint halves of the real set (``extra['real_vs_real']``).
    seed : int
        Random seed. Default: 42.
    """

    name = "mse"
    description = _MSE_DESCRIPTION
    reference = _REFERENCE
    higher_is_better = False
    _report_normalize = True

    def __init__(
        self,
        pairing: str = "nn",
        n_subsample: int = 500,
        normalize: Optional[str] = None,
        baseline: bool = True,
        seed: int = 42,
    ):
        super().__init__(pairing, n_subsample, normalize, baseline, seed)

    def _pair_values(self, R: np.ndarray, S: np.ndarray) -> np.ndarray:
        return pair_mse(R, S)

    def _lead_extra(self, R: np.ndarray, S: np.ndarray, values: np.ndarray) -> Dict[str, float]:
        return {"rmse": float(np.mean(np.sqrt(values)))}


class RMSEMetric(MSEMetric):
    """
    Root mean square error between matched real and synthetic signals, per lead.

    Same parameters as :class:`MSEMetric`. ``extra`` additionally holds ``mse`` and
    ``nrmse`` (RMSE divided by the peak-to-peak range of the real signal).
    """

    name = "rmse"
    description = _RMSE_DESCRIPTION

    def _pair_values(self, R: np.ndarray, S: np.ndarray) -> np.ndarray:
        return np.sqrt(pair_mse(R, S))

    def _lead_extra(self, R: np.ndarray, S: np.ndarray, values: np.ndarray) -> Dict[str, float]:
        span = R.max(axis=1) - R.min(axis=1)
        nrmse = np.where(span > 0, values / np.where(span > 0, span, 1.0), np.nan)
        ok = np.isfinite(nrmse)
        return {
            "mse": float(np.mean(values ** 2)),
            "nrmse": float(nrmse[ok].mean()) if ok.any() else float("nan"),
        }
