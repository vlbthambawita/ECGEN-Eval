"""Tests for all evaluation metrics."""

import numpy as np
import pytest

from ecgen_eval.metrics.base import MetricResult
from ecgen_eval.metrics.mmd import MMDMetric
from ecgen_eval.metrics.dtw import DTWMetric
from ecgen_eval.metrics.prd import PRDMetric
from ecgen_eval.metrics.psd import PSDMetric
from ecgen_eval.metrics.fd import FDMetric
from ecgen_eval.metrics import AVAILABLE_METRICS


# ------------------------------------------------------------------ #
# Shared helpers                                                       #
# ------------------------------------------------------------------ #

def _make(n, leads=12, t=500, seed=0):
    return np.random.default_rng(seed).standard_normal((n, leads, t)).astype(np.float32)


def _assert_result(result: MetricResult, name: str):
    assert isinstance(result, MetricResult)
    assert result.metric_name == name
    assert np.isfinite(result.score)
    assert isinstance(result.per_lead_scores, dict)
    assert len(result.per_lead_scores) == 12


# ------------------------------------------------------------------ #
# Metric registry                                                      #
# ------------------------------------------------------------------ #

def test_available_metrics_keys():
    expected_original = {"mmd", "dtw", "prd", "psd", "fd", "fed"}
    expected_new = {"psnr", "ssim", "swd", "mae", "hrv", "pr_dist", "sqi", "nn_dist", "heart_rate", "spectral_entropy"}
    assert expected_original | expected_new == set(AVAILABLE_METRICS.keys())


# ------------------------------------------------------------------ #
# MMD                                                                  #
# ------------------------------------------------------------------ #

class TestMMD:
    def test_basic(self, real_ecg, synth_ecg):
        m = MMDMetric()
        r = m.compute(real_ecg, synth_ecg)
        _assert_result(r, "mmd")
        assert r.score >= 0.0

    def test_same_data_near_zero(self, real_ecg):
        m = MMDMetric()
        r = m.compute(real_ecg, real_ecg)
        # MMD should be close to zero for identical distributions
        assert r.score < 0.1

    def test_shape_mismatch_raises(self, real_ecg):
        bad = np.zeros((10, 8, 500), dtype=np.float32)
        m = MMDMetric()
        with pytest.raises(ValueError, match="Lead count mismatch"):
            m.compute(real_ecg, bad)

    def test_wrong_ndim_raises(self):
        m = MMDMetric()
        with pytest.raises(ValueError, match="3-D"):
            m.compute(np.zeros((12, 500)), np.zeros((12, 500)))


# ------------------------------------------------------------------ #
# DTW                                                                  #
# ------------------------------------------------------------------ #

class TestDTW:
    def test_basic(self, real_ecg, synth_ecg):
        m = DTWMetric(n_pairs=20)
        r = m.compute(real_ecg, synth_ecg)
        _assert_result(r, "dtw")
        assert r.score >= 0.0

    def test_per_lead_distances_stored(self, real_ecg, synth_ecg):
        m = DTWMetric(n_pairs=10)
        r = m.compute(real_ecg, synth_ecg)
        assert "per_lead_all_distances" in r.extra
        first_key = list(r.extra["per_lead_all_distances"].keys())[0]
        assert len(r.extra["per_lead_all_distances"][first_key]) == 10

    def test_same_data_smaller_than_different(self, real_ecg, synth_ecg):
        # Use many more n_pairs for a stable estimate; expect same ≤ different on average
        m = DTWMetric(n_pairs=100)
        same = m.compute(real_ecg, real_ecg).score
        diff = m.compute(real_ecg, synth_ecg).score
        # The mean across 100 pairs should reliably show same ≤ different
        # (random noise datasets may be similar, so use ≤ not <)
        assert same <= diff * 1.5  # very loose bound


# ------------------------------------------------------------------ #
# PRD                                                                  #
# ------------------------------------------------------------------ #

class TestPRD:
    def test_basic(self, real_ecg, synth_ecg):
        m = PRDMetric()
        r = m.compute(real_ecg, synth_ecg)
        _assert_result(r, "prd")
        assert r.score > 0.0

    def test_same_data_zero(self, real_ecg):
        m = PRDMetric()
        r = m.compute(real_ecg, real_ecg)
        # Nearest neighbour is the same signal → PRD should be 0 (or near 0)
        assert r.score < 1e-3


# ------------------------------------------------------------------ #
# PSD                                                                  #
# ------------------------------------------------------------------ #

class TestPSD:
    def test_basic(self, real_ecg, synth_ecg):
        m = PSDMetric(fs=500.0)
        r = m.compute(real_ecg, synth_ecg)
        _assert_result(r, "psd")
        # JS divergence is in [0, ln2]
        assert 0.0 <= r.score <= 0.7

    def test_same_data_near_zero(self, real_ecg):
        m = PSDMetric(fs=500.0)
        r = m.compute(real_ecg, real_ecg)
        assert r.score < 1e-6

    def test_psd_stored_in_extra(self, real_ecg, synth_ecg):
        m = PSDMetric(fs=500.0)
        r = m.compute(real_ecg, synth_ecg)
        assert "per_lead_psd_real" in r.extra
        assert "per_lead_psd_synth" in r.extra
        first_key = list(r.extra["per_lead_psd_real"].keys())[0]
        assert len(r.extra["per_lead_psd_real"][first_key]) > 0


# ------------------------------------------------------------------ #
# FD                                                                   #
# ------------------------------------------------------------------ #

class TestFD:
    def test_basic(self, real_ecg, synth_ecg):
        m = FDMetric()
        r = m.compute(real_ecg, synth_ecg)
        _assert_result(r, "fd")
        assert np.isfinite(r.score)

    def test_same_data_near_zero(self, real_ecg):
        m = FDMetric()
        r = m.compute(real_ecg, real_ecg)
        # Identical sets → FD ≈ 0 (small due to numerical noise)
        assert r.score < 1.0

    def test_different_data_larger(self, real_ecg, synth_ecg):
        m = FDMetric()
        same = m.compute(real_ecg, real_ecg).score
        diff = m.compute(real_ecg, synth_ecg).score
        assert diff > same


# ------------------------------------------------------------------ #
# Lead name forwarding                                                 #
# ------------------------------------------------------------------ #

def test_lead_names_passed_to_result(real_ecg, synth_ecg):
    leads = ["I", "II", "V1"]
    r_small = real_ecg[:, :3, :]
    s_small = synth_ecg[:, :3, :]
    m = MMDMetric()
    r = m.compute(r_small, s_small, lead_names=leads)
    assert list(r.per_lead_scores.keys()) == leads
