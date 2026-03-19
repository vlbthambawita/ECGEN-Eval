"""Tests for ECG loaders."""

import tempfile
from pathlib import Path

import numpy as np
import pytest

from ecgen_eval.data.loader import load_ecg_folder, load_ecg_npy
from ecgen_eval.data.dataset import ECGDataset, LEADS_12


# ------------------------------------------------------------------ #
# NumPy loader tests                                                   #
# ------------------------------------------------------------------ #

def test_load_npy_3d(tmp_path):
    arr = np.random.default_rng(0).standard_normal((20, 12, 5000)).astype(np.float32)
    f = tmp_path / "test.npy"
    np.save(f, arr)

    ds = load_ecg_npy(f)
    assert ds.n_samples == 20
    assert ds.n_leads == 12
    assert ds.n_timepoints == 5000
    assert ds.lead_names == LEADS_12


def test_load_npy_2d_single(tmp_path):
    arr = np.random.default_rng(0).standard_normal((12, 5000)).astype(np.float32)
    f = tmp_path / "single.npy"
    np.save(f, arr)

    ds = load_ecg_npy(f)
    assert ds.n_samples == 1
    assert ds.n_leads == 12


def test_load_npy_max_samples(tmp_path):
    arr = np.random.default_rng(0).standard_normal((100, 12, 5000)).astype(np.float32)
    f = tmp_path / "big.npy"
    np.save(f, arr)

    ds = load_ecg_npy(f, max_samples=10)
    assert ds.n_samples == 10


def test_load_ecg_folder_npy(tmp_path):
    arr = np.random.default_rng(0).standard_normal((30, 8, 5000)).astype(np.float32)
    np.save(tmp_path / "data.npy", arr)

    ds = load_ecg_folder(tmp_path, fs=500.0, label="test")
    assert ds.n_samples == 30
    assert ds.n_leads == 8
    assert ds.label == "test"


def test_load_npy_with_label(tmp_path):
    arr = np.random.default_rng(0).standard_normal((5, 12, 5000)).astype(np.float32)
    f = tmp_path / "mygen.npy"
    np.save(f, arr)

    ds = load_ecg_npy(f, label="MyGen")
    assert ds.label == "MyGen"


# ------------------------------------------------------------------ #
# CSV loader tests                                                     #
# ------------------------------------------------------------------ #

def test_load_csv_wide(tmp_path):
    import pandas as pd
    arr = np.random.default_rng(0).standard_normal((12, 500)).astype(np.float32)
    pd.DataFrame(arr).to_csv(tmp_path / "rec.csv", header=False, index=False)

    ds = load_ecg_folder(tmp_path, fs=500.0, n_leads=12, n_timepoints=500)
    assert ds.n_samples == 1
    assert ds.n_leads == 12
    assert ds.n_timepoints == 500


def test_load_csv_multi(tmp_path):
    import pandas as pd
    n, l, t = 15, 8, 500
    arr = np.random.default_rng(0).standard_normal((n, l * t)).astype(np.float32)
    pd.DataFrame(arr).to_csv(tmp_path / "multi.csv", header=False, index=False)

    ds = load_ecg_folder(tmp_path, n_leads=l, n_timepoints=t)
    assert ds.n_samples == n
    assert ds.n_leads == l
