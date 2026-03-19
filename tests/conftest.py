"""Shared fixtures for ECGEN-Eval tests."""

import numpy as np
import pytest

from ecgen_eval.data.dataset import ECGDataset, LEADS_12, LEADS_8


RNG = np.random.default_rng(0)


def _make_ecg(n: int = 50, leads: int = 12, t: int = 5000, seed: int = 0) -> np.ndarray:
    """Synthetic ECG-like array (N, L, T) with a rough QRS-like shape."""
    rng = np.random.default_rng(seed)
    base = rng.standard_normal((n, leads, t)).astype(np.float32) * 0.1
    # Add a rough periodic QRS complex
    for i in range(t // 500):
        start = i * 500 + 200
        end = start + 30
        if end < t:
            base[:, :, start:end] += rng.standard_normal((n, leads, 30)).astype(np.float32)
    return base


@pytest.fixture
def real_ecg() -> np.ndarray:
    return _make_ecg(n=60, leads=12, seed=0)


@pytest.fixture
def synth_ecg() -> np.ndarray:
    return _make_ecg(n=50, leads=12, seed=1)


@pytest.fixture
def real_dataset(real_ecg) -> ECGDataset:
    return ECGDataset(
        data=real_ecg,
        lead_names=LEADS_12,
        fs=500.0,
        source_path="/tmp/real",
        label="real",
    )


@pytest.fixture
def synth_dataset(synth_ecg) -> ECGDataset:
    return ECGDataset(
        data=synth_ecg,
        lead_names=LEADS_12,
        fs=500.0,
        source_path="/tmp/synth",
        label="synth",
    )
