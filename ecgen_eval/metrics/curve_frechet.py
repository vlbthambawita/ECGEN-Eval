"""
Discrete (curve) Fréchet distance for ECG evaluation.

This is the Fréchet distance between two **curves**. It is unrelated to the
Fréchet distance between two Gaussians used by ``fd`` and ``fed``; papers call
both "FD".

Reference
---------
Eiter, T., & Mannila, H. (1994).
Computing discrete Fréchet distance.
Technical Report CD-TR 94/64, Christian Doppler Laboratory for Expert Systems,
TU Vienna.

Applied to synthetic ECG:
Delaney, A. M., Brophy, E., & Ward, T. E. (2019).
Synthesis of realistic ECG using generative adversarial networks.
https://arxiv.org/abs/1909.09150

Implementation notes
--------------------
For curves P = (p_1..p_n) and Q = (q_1..q_m) the coupling measure is

  c(i, j) = max( min(c(i−1, j), c(i−1, j−1), c(i, j−1)),  d(p_i, q_j) )

and the discrete Fréchet distance is c(n, m): the smallest achievable *maximum*
gap when both curves are traversed monotonically.

* Signals are decimated to at most ``max_len`` points (the DP is O(n·m)).
* ``time_weight = 0`` (default): d = |x_i − y_j|, in signal units.
  ``time_weight > 0``: points are (time_weight · t_seconds, amplitude) with
  Euclidean d, so warping in time has a cost.
* Pairs are selected with ``pairing`` on the decimated signals; the distance is
  then computed for each matched pair, vectorised over pairs and anti-diagonals.
"""

from __future__ import annotations

from typing import Dict

import numpy as np

from ecgen_eval.metrics._pairwise import PairwiseSignalMetric

_REFERENCE = (
    "Eiter, T., & Mannila, H. (1994). Computing discrete Fréchet distance. Technical Report "
    "CD-TR 94/64, Christian Doppler Laboratory for Expert Systems, TU Vienna."
)

_DESCRIPTION = (
    "Curve Fréchet Distance: discrete Fréchet distance between real ECG waveforms and their "
    "matched synthetic waveforms, computed per lead. Lower is better (0 = identical curves)."
)


def discrete_frechet(
    P: np.ndarray, Q: np.ndarray, time_weight: float = 0.0, dt: float = 1.0
) -> np.ndarray:
    """
    Discrete Fréchet distance for a batch of curve pairs.

    Parameters
    ----------
    P : (M, n) or (n,) amplitudes of the first curves
    Q : (M, m) or (m,) amplitudes of the second curves
    time_weight : weight of the time axis; 0 compares amplitudes only
    dt : spacing between samples in seconds (used when ``time_weight > 0``)

    Returns
    -------
    (M,) array of distances (a float for 1-D inputs).
    """
    single = np.ndim(P) == 1
    P = np.atleast_2d(np.asarray(P, dtype=np.float64))
    Q = np.atleast_2d(np.asarray(Q, dtype=np.float64))
    M, n = P.shape
    m = Q.shape[1]
    tw = float(time_weight) * float(dt)

    def dist(i: np.ndarray, j: np.ndarray) -> np.ndarray:
        d = np.abs(P[:, i] - Q[:, j])
        if tw > 0:
            d = np.sqrt(d ** 2 + (tw * (i - j)) ** 2)
        return d

    # Anti-diagonal k holds cells (i, k - i). Arrays are indexed by i + 1 so that
    # index 0 is a permanent +inf border for "i - 1" look-ups.
    prev1 = np.full((M, n + 1), np.inf)  # diagonal k - 1
    prev2 = np.full((M, n + 1), np.inf)  # diagonal k - 2
    for k in range(n + m - 1):
        i = np.arange(max(0, k - m + 1), min(k, n - 1) + 1)
        d = dist(i, k - i)
        cur = np.full((M, n + 1), np.inf)
        if k == 0:
            cur[:, 1] = d[:, 0]
        else:
            best = np.minimum(np.minimum(prev1[:, i], prev1[:, i + 1]), prev2[:, i])
            cur[:, i + 1] = np.maximum(best, d)
        prev2, prev1 = prev1, cur
    out = prev1[:, n]
    return float(out[0]) if single else out


def discrete_frechet_reference(
    p: np.ndarray, q: np.ndarray, time_weight: float = 0.0, dt: float = 1.0
) -> float:
    """Plain O(n·m) double loop for one pair. Slow; used to test :func:`discrete_frechet`."""
    p = np.asarray(p, dtype=np.float64)
    q = np.asarray(q, dtype=np.float64)
    n, m = len(p), len(q)
    tw = float(time_weight) * float(dt)
    ca = np.empty((n, m))
    for i in range(n):
        for j in range(m):
            d = abs(p[i] - q[j])
            if tw > 0:
                d = float(np.hypot(d, tw * (i - j)))
            if i == 0 and j == 0:
                ca[i, j] = d
            elif i == 0:
                ca[i, j] = max(ca[i, j - 1], d)
            elif j == 0:
                ca[i, j] = max(ca[i - 1, j], d)
            else:
                ca[i, j] = max(min(ca[i - 1, j], ca[i - 1, j - 1], ca[i, j - 1]), d)
    return float(ca[-1, -1])


class CurveFrechetMetric(PairwiseSignalMetric):
    """
    Discrete Fréchet distance between matched real and synthetic curves, per lead.

    Parameters
    ----------
    pairing : {'nn', 'paired', 'mean'}
        How real and synthetic signals are matched. Default: 'nn' (nearest synthetic
        signal by Euclidean distance on the decimated signals).
    n_pairs : int
        Max real signals scored per lead. Default: 100.
    max_len : int
        Signals are decimated to at most this many points. Default: 500.
    time_weight : float
        Weight of the time axis (seconds) in the point distance. Default: 0
        (amplitude only).
    fs : float
        Sampling rate in Hz (used when ``time_weight > 0``).
    n_candidates : int
        Max synthetic signals searched for the nearest neighbour. Default: 500.
    baseline : bool
        Also score two disjoint halves of the real set (``extra['real_vs_real']``).
    seed : int
        Random seed. Default: 42.
    """

    name = "curve_frechet"
    description = _DESCRIPTION
    reference = _REFERENCE
    higher_is_better = False

    def __init__(
        self,
        pairing: str = "nn",
        n_pairs: int = 100,
        max_len: int = 500,
        time_weight: float = 0.0,
        fs: float = 500.0,
        n_candidates: int = 500,
        baseline: bool = True,
        seed: int = 42,
    ):
        super().__init__(pairing, n_pairs, None, baseline, seed)
        if max_len < 2:
            raise ValueError("max_len must be at least 2.")
        self.n_pairs = n_pairs
        self.max_len = max_len
        self.time_weight = time_weight
        self.fs = fs
        self.n_candidates = n_candidates
        self._stride = 1

    def _prepare(self, X: np.ndarray) -> np.ndarray:
        self._stride = max(1, int(np.ceil(X.shape[1] / self.max_len)))
        return np.asarray(X[:, :: self._stride], dtype=np.float64)

    def _pair_values(self, R: np.ndarray, S: np.ndarray) -> np.ndarray:
        dt = self._stride / self.fs
        out = np.empty(R.shape[0])
        for start in range(0, R.shape[0], 64):
            sl = slice(start, start + 64)
            out[sl] = discrete_frechet(R[sl], S[sl], self.time_weight, dt)
        return out

    def _lead_extra(self, R: np.ndarray, S: np.ndarray, values: np.ndarray) -> Dict[str, float]:
        return {
            "n_points": float(R.shape[1]),
            "effective_fs": float(self.fs / self._stride),
            "time_weight": float(self.time_weight),
        }
