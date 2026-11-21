"""
Pairing helpers shared by the waveform-level fidelity metrics.

Papers report point-wise metrics (MSE, Pearson, ...) under three protocols whose
numbers are not comparable, so the protocol is an explicit ``pairing`` choice:

``"nn"``
    Each real signal is compared with its nearest synthetic signal. Valid for
    unpaired generation and the default everywhere.
``"paired"``
    Real signal *i* is compared with synthetic signal *i* (reconstruction,
    lead synthesis, PPG-to-ECG translation). Needs equal sample counts.
``"mean"``
    The mean real waveform is compared with the mean synthetic waveform. Only
    meaningful for beat-aligned inputs.

All functions work on one lead at a time: arrays of shape ``(N, T)``.
"""

from __future__ import annotations

from typing import Callable, Optional, Tuple

import numpy as np

PAIRINGS = ("nn", "paired", "mean")


def check_pairing(pairing: str) -> str:
    """Validate and normalise a pairing name."""
    key = str(pairing).lower()
    if key not in PAIRINGS:
        raise ValueError(f"Unknown pairing {pairing!r}. Choose one of {PAIRINGS}.")
    return key


def subsample(X: np.ndarray, n: Optional[int], rng: np.random.Generator) -> np.ndarray:
    """Return at most ``n`` rows of ``X``, drawn without replacement."""
    if n is None or X.shape[0] <= n:
        return X
    idx = rng.choice(X.shape[0], size=n, replace=False)
    return X[idx]


def subsample_paired(
    R: np.ndarray, S: np.ndarray, n: Optional[int], rng: np.random.Generator
) -> Tuple[np.ndarray, np.ndarray]:
    """Subsample two index-aligned arrays with the same row indices."""
    if R.shape[0] != S.shape[0]:
        raise ValueError(
            f"pairing='paired' needs the same number of real and synthetic recordings, "
            f"got {R.shape[0]} and {S.shape[0]}."
        )
    if n is None or R.shape[0] <= n:
        return R, S
    idx = rng.choice(R.shape[0], size=n, replace=False)
    return R[idx], S[idx]


def nearest_neighbour(R: np.ndarray, S: np.ndarray, chunk: int = 256) -> np.ndarray:
    """
    Index of the nearest row of ``S`` (Euclidean distance) for every row of ``R``.

    Uses ``‖s‖² − 2·r·s`` in chunks, so memory stays at ``chunk × N_s`` instead of
    ``N_r × N_s × T``.
    """
    R = np.asarray(R, dtype=np.float64)
    S = np.asarray(S, dtype=np.float64)
    s_sq = np.einsum("ij,ij->i", S, S)
    out = np.empty(R.shape[0], dtype=np.int64)
    for start in range(0, R.shape[0], chunk):
        block = R[start:start + chunk]
        out[start:start + chunk] = np.argmin(s_sq[None, :] - 2.0 * (block @ S.T), axis=1)
    return out


def matched_pairs(
    R: np.ndarray,
    S: np.ndarray,
    pairing: str = "nn",
    n_subsample: Optional[int] = 500,
    rng: Optional[np.random.Generator] = None,
    key: Optional[Callable[[np.ndarray], np.ndarray]] = None,
    n_candidates: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Return row-aligned ``(R_m, S_m)`` for one lead.

    Parameters
    ----------
    R, S : (N_r, T), (N_s, T)
    pairing : 'nn' | 'paired' | 'mean'
    n_subsample : max real rows used (and synthetic rows, unless ``n_candidates``)
    rng : random generator; real rows are drawn first, then synthetic rows
    key : optional transform applied before the nearest-neighbour search only
        (e.g. z-normalisation, so the neighbour is the best-correlated signal)
    n_candidates : max synthetic rows searched in 'nn' mode (default ``n_subsample``)
    """
    pairing = check_pairing(pairing)
    if rng is None:
        rng = np.random.default_rng(0)
    if R.shape[0] == 0 or S.shape[0] == 0:
        raise ValueError("Both real and synthetic sets need at least one recording.")

    if pairing == "paired":
        return subsample_paired(R, S, n_subsample, rng)

    R = subsample(R, n_subsample, rng)
    S = subsample(S, n_candidates if n_candidates is not None else n_subsample, rng)
    if pairing == "mean":
        return R.mean(axis=0, keepdims=True), S.mean(axis=0, keepdims=True)

    idx = nearest_neighbour(key(R), key(S)) if key is not None else nearest_neighbour(R, S)
    return R, S[idx]


def split_half(R: np.ndarray, rng: np.random.Generator) -> Tuple[np.ndarray, np.ndarray]:
    """Two disjoint, equally sized random halves of ``R`` (for a real-vs-real baseline)."""
    half = R.shape[0] // 2
    perm = rng.permutation(R.shape[0])
    return R[perm[:half]], R[perm[half:2 * half]]
