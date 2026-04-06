"""
Shared Fréchet Distance math used by FDMetric and FEDMetric.

FD = ‖μ_X − μ_Y‖² + Tr(Σ_X + Σ_Y − 2·(Σ_X Σ_Y)^½)
"""

from __future__ import annotations

import numpy as np


def frechet_distance(X: np.ndarray, Y: np.ndarray, eps: float = 1e-6) -> float:
    """
    Compute the Fréchet Distance between two sets of feature vectors.

    Parameters
    ----------
    X : np.ndarray, shape (N, D)
        Feature matrix for the first distribution (e.g. real).
    Y : np.ndarray, shape (M, D)
        Feature matrix for the second distribution (e.g. synthetic).
    eps : float
        Small value added to the covariance diagonal for numerical stability.

    Returns
    -------
    float
        Fréchet Distance (lower is better; 0 means identical distributions).
    """
    mu1, sigma1 = X.mean(axis=0), np.cov(X, rowvar=False)
    mu2, sigma2 = Y.mean(axis=0), np.cov(Y, rowvar=False)

    # Ensure 2-D even when D == 1
    if sigma1.ndim == 0:
        sigma1 = sigma1.reshape(1, 1)
    if sigma2.ndim == 0:
        sigma2 = sigma2.reshape(1, 1)

    n_feat = mu1.shape[0]
    sigma1 = sigma1 + eps * np.eye(n_feat)
    sigma2 = sigma2 + eps * np.eye(n_feat)

    diff = mu1 - mu2
    mean_sq = float(np.dot(diff, diff))

    sqrt_sigma = _matrix_sqrt(sigma1 @ sigma2)
    trace_term = float(np.trace(sigma1 + sigma2 - 2.0 * sqrt_sigma))
    return mean_sq + trace_term


def _matrix_sqrt(M: np.ndarray) -> np.ndarray:
    """Symmetric matrix square root via eigendecomposition."""
    M = (M + M.T) / 2.0
    eigenvalues, eigenvectors = np.linalg.eigh(M)
    eigenvalues = np.maximum(eigenvalues, 0.0)
    return eigenvectors @ np.diag(np.sqrt(eigenvalues)) @ eigenvectors.T
