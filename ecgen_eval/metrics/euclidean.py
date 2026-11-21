"""
Time-domain Euclidean distance for ECG evaluation.

Reference
---------
Wang, X., Mueen, A., Ding, H., Trajcevski, G., Scheuermann, P., & Keogh, E. (2013).
Experimental comparison of representation methods and distance measures for time
series data. *Data Mining and Knowledge Discovery*, 26, 275–309.
https://doi.org/10.1007/s10618-012-0250-5

Implementation notes
--------------------
Per lead, real and synthetic signals are matched according to ``pairing`` and

  ED = sqrt( Σ_t (real[t] − synth[t])² ) = sqrt(T) · RMSE

is averaged over pairs. ED grows with sqrt(T), so it is only comparable between
recordings of the same length; ``extra['length_normalised']`` (= ED / sqrt(T), the
RMSE) removes that dependence.

This is a waveform distance. :class:`~ecgen_eval.metrics.nn_dist.NNDistMetric` also
uses a nearest-neighbour Euclidean distance, but in a 7-feature statistical space
and to detect memorisation.
"""

from __future__ import annotations

from typing import Dict, Optional

import numpy as np

from ecgen_eval.metrics._pairwise import PairwiseSignalMetric
from ecgen_eval.metrics.mse import pair_mse

_REFERENCE = (
    "Wang, X., Mueen, A., Ding, H., Trajcevski, G., Scheuermann, P., & Keogh, E. (2013). "
    "Experimental comparison of representation methods and distance measures for time series "
    "data. Data Mining and Knowledge Discovery, 26, 275–309. "
    "https://doi.org/10.1007/s10618-012-0250-5"
)

_DESCRIPTION = (
    "Euclidean Distance: L2 distance in the time domain between real ECGs and their matched "
    "synthetic ECGs, computed per lead. Lower is better (0 = identical); grows with signal length."
)


class EuclideanMetric(PairwiseSignalMetric):
    """
    Euclidean (L2) distance between matched real and synthetic signals, per lead.

    Parameters
    ----------
    pairing : {'nn', 'paired', 'mean'}
        How real and synthetic signals are matched. Default: 'nn'.
    n_subsample : int
        Max recordings per set. Default: 500.
    normalize : {None, 'zscore', 'minmax'}
        Per-recording, per-lead normalisation applied before matching. Default: None.
    baseline : bool
        Also score two disjoint halves of the real set (``extra['real_vs_real']``).
    seed : int
        Random seed. Default: 42.
    """

    name = "euclidean"
    description = _DESCRIPTION
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
        return np.sqrt(pair_mse(R, S) * R.shape[1])

    def _lead_extra(self, R: np.ndarray, S: np.ndarray, values: np.ndarray) -> Dict[str, float]:
        T = R.shape[1]
        return {"length_normalised": float(np.mean(values) / np.sqrt(T)), "n_timepoints": float(T)}
