"""Two-sample statistics shared by ``ks_test`` and the clinical-feature comparison."""

from __future__ import annotations

from typing import Tuple

import numpy as np


def ks_statistic(a: np.ndarray, b: np.ndarray) -> float:
    """
    Two-sample Kolmogorov–Smirnov statistic ``D = sup_x |F_a(x) − F_b(x)|``.

    NaNs are ignored. Returns NaN if either sample is empty.
    """
    a = np.sort(np.asarray(a, dtype=np.float64).ravel())
    b = np.sort(np.asarray(b, dtype=np.float64).ravel())
    a = a[~np.isnan(a)]
    b = b[~np.isnan(b)]
    if a.size == 0 or b.size == 0:
        return float("nan")
    pooled = np.concatenate([a, b])
    cdf_a = np.searchsorted(a, pooled, side="right") / a.size
    cdf_b = np.searchsorted(b, pooled, side="right") / b.size
    return float(np.max(np.abs(cdf_a - cdf_b)))


def ks_pvalue_asymptotic(d: float, n: int, m: int) -> float:
    """
    Asymptotic two-sided p-value of the two-sample KS statistic (Kolmogorov
    distribution with the small-sample correction of Stephens, 1970).
    """
    if not np.isfinite(d) or n == 0 or m == 0:
        return float("nan")
    en = np.sqrt(n * m / (n + m))
    lam = (en + 0.12 + 0.11 / en) * d
    if lam < 1e-3:
        return 1.0
    j = np.arange(1, 101)
    p = 2.0 * np.sum((-1.0) ** (j - 1) * np.exp(-2.0 * (j * lam) ** 2))
    return float(np.clip(p, 0.0, 1.0))


def ks_2samp(a: np.ndarray, b: np.ndarray) -> Tuple[float, float, str]:
    """
    Two-sample KS test. Returns ``(D, p, method)``.

    ``D`` is always computed with NumPy. The p-value comes from
    ``scipy.stats.ks_2samp`` when SciPy is installed (``method='scipy'``) and from
    the asymptotic distribution otherwise (``method='asymptotic'``).
    """
    a = np.asarray(a, dtype=np.float64).ravel()
    b = np.asarray(b, dtype=np.float64).ravel()
    a = a[~np.isnan(a)]
    b = b[~np.isnan(b)]
    d = ks_statistic(a, b)
    if not np.isfinite(d):
        return d, float("nan"), "none"
    try:
        from scipy.stats import ks_2samp as _scipy_ks

        return d, float(_scipy_ks(a, b).pvalue), "scipy"
    except ImportError:
        return d, ks_pvalue_asymptotic(d, a.size, b.size), "asymptotic"


def mann_whitney_pvalue(a: np.ndarray, b: np.ndarray) -> float:
    """Two-sided Mann–Whitney U p-value; NaN when SciPy is missing or a sample is empty."""
    a = np.asarray(a, dtype=np.float64).ravel()
    b = np.asarray(b, dtype=np.float64).ravel()
    a = a[~np.isnan(a)]
    b = b[~np.isnan(b)]
    if a.size == 0 or b.size == 0:
        return float("nan")
    try:
        from scipy.stats import mannwhitneyu
    except ImportError:
        return float("nan")
    if np.all(a == a[0]) and np.all(b == a[0]):
        return 1.0
    return float(mannwhitneyu(a, b, alternative="two-sided").pvalue)


def adjust_pvalues(p: np.ndarray, method: str = "holm") -> np.ndarray:
    """
    Multiple-testing adjustment of a flat array of p-values.

    ``method``: 'holm' (step-down, default), 'bonferroni' or 'none'. NaNs are kept
    and do not count as tests.
    """
    p = np.asarray(p, dtype=np.float64)
    out = np.full(p.shape, np.nan)
    ok = np.isfinite(p)
    k = int(ok.sum())
    if k == 0 or method == "none":
        out[ok] = p[ok]
        return out
    vals = p[ok]
    if method == "bonferroni":
        adj = np.minimum(vals * k, 1.0)
    elif method == "holm":
        order = np.argsort(vals)
        stepped = np.maximum.accumulate(vals[order] * (k - np.arange(k)))
        adj = np.empty(k)
        adj[order] = np.minimum(stepped, 1.0)
    else:
        raise ValueError(f"Unknown correction {method!r}. Choose 'holm', 'bonferroni' or 'none'.")
    out[ok] = adj
    return out


def cohens_d(a: np.ndarray, b: np.ndarray) -> float:
    """Standardised mean difference ``(mean(b) − mean(a)) / pooled SD``; NaNs ignored."""
    a = np.asarray(a, dtype=np.float64).ravel()
    b = np.asarray(b, dtype=np.float64).ravel()
    a = a[~np.isnan(a)]
    b = b[~np.isnan(b)]
    if a.size < 2 or b.size < 2:
        return float("nan")
    pooled = np.sqrt(((a.size - 1) * a.var(ddof=1) + (b.size - 1) * b.var(ddof=1))
                     / (a.size + b.size - 2))
    if pooled <= 0:
        return 0.0 if a.mean() == b.mean() else float("nan")
    return float((b.mean() - a.mean()) / pooled)
