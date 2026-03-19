"""Tests for ECGDataset."""

import numpy as np
import pytest

from ecgen_eval.data.dataset import ECGDataset, LEADS_12, LEADS_8


def test_properties(real_dataset):
    ds = real_dataset
    assert ds.n_samples == 60
    assert ds.n_leads == 12
    assert ds.n_timepoints == 5000
    assert ds.duration_sec == pytest.approx(10.0)
    assert len(ds.time_axis) == 5000


def test_select_leads(real_dataset):
    sub = real_dataset.select_leads(["I", "II", "V1"])
    assert sub.n_leads == 3
    assert sub.lead_names == ["I", "II", "V1"]
    assert sub.data.shape == (60, 3, 5000)


def test_sample(real_dataset):
    sub = real_dataset.sample(10)
    assert sub.n_samples == 10


def test_repr(real_dataset):
    s = repr(real_dataset)
    assert "real" in s
    assert "60" in s
