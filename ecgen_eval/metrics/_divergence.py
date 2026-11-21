"""Kullback–Leibler and Jensen–Shannon divergences shared by several metrics."""

from __future__ import annotations

import numpy as np


def js_divergence(p: np.ndarray, q: np.ndarray) -> float:
    """
    Jensen–Shannon divergence between two non-negative vectors (natural log).

    Both vectors are normalised to sum to 1. Range ``[0, ln 2]``.
    """
    p = p / (p.sum() + 1e-12)
    q = q / (q.sum() + 1e-12)
    m = 0.5 * (p + q)
    with np.errstate(divide="ignore", invalid="ignore"):  # empty bins are masked by where()
        kl_pm = np.sum(np.where(p > 0, p * np.log(p / (m + 1e-12)), 0.0))
        kl_qm = np.sum(np.where(q > 0, q * np.log(q / (m + 1e-12)), 0.0))
    return float(0.5 * kl_pm + 0.5 * kl_qm)


def kl_divergence(p: np.ndarray, q: np.ndarray, eps: float = 1e-10) -> float:
    """
    Kullback–Leibler divergence ``KL(p ‖ q)`` between two non-negative vectors
    (natural log). ``eps`` is added to every bin before normalisation so that the
    result stays finite when ``q`` has empty bins.
    """
    p = np.asarray(p, dtype=np.float64) + eps
    q = np.asarray(q, dtype=np.float64) + eps
    p = p / p.sum()
    q = q / q.sum()
    return float(np.sum(p * np.log(p / q)))


def js_from_samples(p_vals: np.ndarray, q_vals: np.ndarray, n_bins: int = 50) -> float:
    """
    Jensen–Shannon divergence between two samples of a scalar quantity.

    Both samples are binned into ``n_bins`` equal bins spanning their pooled range.
    NaNs are ignored; an empty or constant sample gives 0. Range ``[0, ln 2]``.
    """
    p_vals = np.asarray(p_vals)  # keep the input dtype: scores must not change
    q_vals = np.asarray(q_vals)
    p_vals = p_vals[~np.isnan(p_vals)]
    q_vals = q_vals[~np.isnan(q_vals)]
    if len(p_vals) == 0 or len(q_vals) == 0:
        return 0.0

    lo = min(p_vals.min(), q_vals.min())
    hi = max(p_vals.max(), q_vals.max())
    if hi <= lo:
        return 0.0

    bins = np.linspace(lo, hi, n_bins + 1)
    p_hist, _ = np.histogram(p_vals, bins=bins, density=True)
    q_hist, _ = np.histogram(q_vals, bins=bins, density=True)

    p_hist = p_hist + 1e-10
    q_hist = q_hist + 1e-10
    p_hist /= p_hist.sum()
    q_hist /= q_hist.sum()

    m = 0.5 * (p_hist + q_hist)
    eps = 1e-15
    js = 0.5 * (
        np.sum(p_hist * np.log((p_hist + eps) / (m + eps)))
        + np.sum(q_hist * np.log((q_hist + eps) / (m + eps)))
    )
    return float(np.clip(js, 0.0, np.log(2)))
