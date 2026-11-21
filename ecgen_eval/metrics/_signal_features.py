"""Handcrafted per-recording signal descriptors shared by several metrics."""

from __future__ import annotations

import numpy as np

#: Names of the columns returned by :func:`stat_features`.
STAT_FEATURE_NAMES = (
    "mean", "std", "rms", "max_abs", "energy", "zero_crossing_rate", "lag1_autocorr",
)

#: Names of the columns returned by :func:`extended_features`.
EXTENDED_FEATURE_NAMES = (
    "mean", "std", "rms", "energy", "max_abs", "skewness", "kurtosis",
    "zero_crossing_rate", "lag1_autocorr", "spectral_centroid", "spectral_bandwidth",
)


def stat_features(signals: np.ndarray) -> np.ndarray:
    """
    7-feature statistical descriptor per recording (used by mmd, swd, pr_dist,
    nn_dist, ks_test).

    Input : (N, T)
    Output: (N, 7) float32 — columns as in :data:`STAT_FEATURE_NAMES`.
    """
    mean_amp = np.mean(signals, axis=1)
    std_amp = np.std(signals, axis=1)
    rms = np.sqrt(np.mean(signals ** 2, axis=1))
    max_abs = np.max(np.abs(signals), axis=1)
    energy = np.sum(signals ** 2, axis=1) / signals.shape[1]
    # Zero-crossing rate
    signs = np.sign(signals)
    zcr = np.sum(np.abs(np.diff(signs, axis=1)), axis=1) / (2.0 * (signals.shape[1] - 1))
    # Lag-1 autocorrelation
    mu = mean_amp[:, None]
    centered = signals - mu
    ac = np.sum(centered[:, :-1] * centered[:, 1:], axis=1) / (
        np.sum(centered ** 2, axis=1) + 1e-9
    )

    feats = np.stack([mean_amp, std_amp, rms, max_abs, energy, zcr, ac], axis=1)
    return feats.astype(np.float32)


def extended_features(signals: np.ndarray) -> np.ndarray:
    """
    11-feature descriptor per recording (used by fd, c2st and the embedding plots).

    Input : (N, T)
    Output: (N, 11) float64 — columns as in :data:`EXTENDED_FEATURE_NAMES`.
    """
    x = signals.astype(np.float64)
    T = x.shape[1]

    mean = np.mean(x, axis=1)
    std = np.std(x, axis=1) + 1e-9
    rms = np.sqrt(np.mean(x ** 2, axis=1))
    energy = np.sum(x ** 2, axis=1) / T
    max_abs = np.max(np.abs(x), axis=1)

    # Skewness and kurtosis (standardised central moments)
    centred = x - mean[:, None]
    skew = np.mean((centred / std[:, None]) ** 3, axis=1)
    kurt = np.mean((centred / std[:, None]) ** 4, axis=1)

    # Zero-crossing rate
    signs = np.sign(x)
    zcr = np.sum(np.abs(np.diff(signs, axis=1)), axis=1) / (2.0 * (T - 1))

    # Lag-1 autocorrelation
    ac = np.sum(centred[:, :-1] * centred[:, 1:], axis=1) / (
        np.sum(centred ** 2, axis=1) + 1e-9
    )

    # Spectral centroid and bandwidth (from magnitude FFT)
    fft_mag = np.abs(np.fft.rfft(x, axis=1))
    freqs = np.arange(fft_mag.shape[1], dtype=np.float64)
    total_power = np.sum(fft_mag, axis=1) + 1e-9
    spectral_centroid = np.sum(fft_mag * freqs[None, :], axis=1) / total_power
    spectral_bandwidth = np.sqrt(
        np.sum(fft_mag * (freqs[None, :] - spectral_centroid[:, None]) ** 2, axis=1)
        / total_power
    )

    feats = np.stack([
        mean, std, rms, energy, max_abs, skew, kurt,
        zcr, ac, spectral_centroid, spectral_bandwidth
    ], axis=1)
    return feats
