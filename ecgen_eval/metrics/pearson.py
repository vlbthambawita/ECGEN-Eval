"""
Pearson correlation between real and synthetic ECG waveforms.

Reference
---------
Pearson, K. (1895).
Note on regression and inheritance in the case of two parents.
*Proceedings of the Royal Society of London*, 58, 240–242.
https://doi.org/10.1098/rspl.1895.0041

Implementation notes
--------------------
Per lead, real and synthetic signals are matched according to ``pairing`` and

  r = Σ (x_r − mean(x_r)) (x_s − mean(x_s)) / (‖x_r − mean(x_r)‖ · ‖x_s − mean(x_s)‖)

is averaged over pairs. In ``'nn'`` mode the neighbour is the synthetic signal with
the **highest correlation** (nearest neighbour after z-normalisation), not the one
with the smallest raw Euclidean distance.

Signals with zero variance (flat leads) have no defined correlation; those pairs are
skipped and counted in ``extra['n_skipped']``.

With ``max_lag_ms > 0`` the maximum normalised cross-correlation within
±``max_lag_ms`` is reported in ``extra`` (``xcorr_max``, ``best_lag_ms``). The
primary score stays the zero-lag correlation.

:class:`~ecgen_eval.metrics.sqi.SQIMetric` also uses Pearson correlation, but
against the mean real template instead of sample to sample.
"""

from __future__ import annotations

from typing import Dict

import numpy as np

from ecgen_eval.metrics._pairwise import PairwiseSignalMetric

_REFERENCE = (
    "Pearson, K. (1895). Note on regression and inheritance in the case of two parents. "
    "Proceedings of the Royal Society of London, 58, 240–242. "
    "https://doi.org/10.1098/rspl.1895.0041"
)

_DESCRIPTION = (
    "Pearson Correlation: mean correlation coefficient between real ECGs and their matched "
    "synthetic ECGs, computed per lead. Higher is better (1 = identical shape)."
)


def unit_rows(X: np.ndarray, center: bool) -> np.ndarray:
    """
    Scale rows to unit L2 norm, optionally after removing the row mean.

    The dot product of two such rows is their Pearson correlation (``center=True``)
    or cosine similarity (``center=False``). Rows with zero norm become NaN.
    """
    X = np.asarray(X, dtype=np.float64)
    if center:
        X = X - X.mean(axis=1, keepdims=True)
    norm = np.sqrt(np.einsum("ij,ij->i", X, X))
    with np.errstate(invalid="ignore", divide="ignore"):
        return X / np.where(norm > 1e-12, norm, np.nan)[:, None]


class PearsonMetric(PairwiseSignalMetric):
    """
    Pearson correlation between matched real and synthetic signals, per lead.

    Parameters
    ----------
    pairing : {'nn', 'paired', 'mean'}
        How real and synthetic signals are matched. Default: 'nn' (best-correlated
        synthetic signal of the same lead).
    n_subsample : int
        Max recordings per set. Default: 500.
    max_lag_ms : float
        If > 0, also report the maximum cross-correlation within ±``max_lag_ms``.
    fs : float
        Sampling rate in Hz (only used to convert ``max_lag_ms`` to samples).
    baseline : bool
        Also score two disjoint halves of the real set (``extra['real_vs_real']``).
    seed : int
        Random seed. Default: 42.
    """

    name = "pearson"
    description = _DESCRIPTION
    reference = _REFERENCE
    higher_is_better = True

    def __init__(
        self,
        pairing: str = "nn",
        n_subsample: int = 500,
        max_lag_ms: float = 0.0,
        fs: float = 500.0,
        baseline: bool = True,
        seed: int = 42,
    ):
        super().__init__(pairing, n_subsample, None, baseline, seed)
        self.max_lag_ms = max_lag_ms
        self.fs = fs

    def _match_key(self, X: np.ndarray) -> np.ndarray:
        return np.nan_to_num(unit_rows(X, center=True))

    def _pair_values(self, R: np.ndarray, S: np.ndarray) -> np.ndarray:
        return np.einsum("ij,ij->i", unit_rows(R, center=True), unit_rows(S, center=True))

    def _lead_extra(self, R: np.ndarray, S: np.ndarray, values: np.ndarray) -> Dict[str, float]:
        max_lag = int(round(self.max_lag_ms * self.fs / 1000.0))
        if max_lag <= 0:
            return {}
        zr, zs = unit_rows(R, center=True), unit_rows(S, center=True)
        T = zr.shape[1]
        max_lag = min(max_lag, T - 1)
        lags = np.arange(-max_lag, max_lag + 1)
        xc = np.empty((len(lags), zr.shape[0]))
        for k, lag in enumerate(lags):
            # lag > 0: the synthetic signal is `lag` samples late.
            if lag >= 0:
                xc[k] = np.einsum("ij,ij->i", zr[:, :T - lag], zs[:, lag:])
            else:
                xc[k] = np.einsum("ij,ij->i", zr[:, -lag:], zs[:, :T + lag])
        ok = np.isfinite(xc).all(axis=0)
        if not ok.any():
            return {"xcorr_max": float("nan"), "best_lag_ms": float("nan")}
        best = np.argmax(xc[:, ok], axis=0)
        return {
            "xcorr_max": float(xc[:, ok].max(axis=0).mean()),
            "best_lag_ms": float(np.mean(lags[best]) * 1000.0 / self.fs),
        }
