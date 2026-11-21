"""
Cosine similarity between real and synthetic ECG waveforms.

Reference
---------
Singhal, A. (2001).
Modern information retrieval: A brief overview.
*IEEE Data Engineering Bulletin*, 24(4), 35–43.

Implementation notes
--------------------
Per lead, real and synthetic signals are matched according to ``pairing`` and

  cos = Σ x_r[t] · x_s[t] / (‖x_r‖ · ‖x_s‖)

is averaged over pairs. In ``'nn'`` mode the neighbour is the synthetic signal with
the highest cosine similarity.

Cosine similarity is Pearson correlation without mean removal, so a shared baseline
offset raises it. All-zero signals are skipped and counted in
``extra['n_skipped']``.
"""

from __future__ import annotations

import numpy as np

from ecgen_eval.metrics._pairwise import PairwiseSignalMetric
from ecgen_eval.metrics.pearson import unit_rows

_REFERENCE = (
    "Singhal, A. (2001). Modern information retrieval: A brief overview. "
    "IEEE Data Engineering Bulletin, 24(4), 35–43."
)

_DESCRIPTION = (
    "Cosine Similarity: mean cosine of the angle between real ECGs and their matched synthetic "
    "ECGs as vectors, computed per lead. Higher is better (1 = same direction)."
)


class CosineMetric(PairwiseSignalMetric):
    """
    Cosine similarity between matched real and synthetic signals, per lead.

    Parameters
    ----------
    pairing : {'nn', 'paired', 'mean'}
        How real and synthetic signals are matched. Default: 'nn' (most similar
        synthetic signal of the same lead).
    n_subsample : int
        Max recordings per set. Default: 500.
    baseline : bool
        Also score two disjoint halves of the real set (``extra['real_vs_real']``).
    seed : int
        Random seed. Default: 42.
    """

    name = "cosine"
    description = _DESCRIPTION
    reference = _REFERENCE
    higher_is_better = True

    def __init__(
        self,
        pairing: str = "nn",
        n_subsample: int = 500,
        baseline: bool = True,
        seed: int = 42,
    ):
        super().__init__(pairing, n_subsample, None, baseline, seed)

    def _match_key(self, X: np.ndarray) -> np.ndarray:
        return np.nan_to_num(unit_rows(X, center=False))

    def _pair_values(self, R: np.ndarray, S: np.ndarray) -> np.ndarray:
        return np.einsum("ij,ij->i", unit_rows(R, center=False), unit_rows(S, center=False))
