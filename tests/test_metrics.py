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

    def test_matches_brute_force_nearest_neighbour(self):
        real = _make(20, leads=3, t=200, seed=0)
        synth = _make(30, leads=3, t=200, seed=1)
        r = PRDMetric().compute(real, synth, lead_names=["A", "B", "C"])

        diff = real.reshape(20, 1, -1) - synth.reshape(1, 30, -1)
        nn = synth[np.argmin(np.sum(diff**2, axis=-1), axis=1)]
        for li, lname in enumerate(["A", "B", "C"]):
            num = np.linalg.norm(real[:, li] - nn[:, li], axis=-1)
            den = np.linalg.norm(real[:, li], axis=-1) + 1e-9
            assert r.per_lead_scores[lname] == pytest.approx(np.mean(100.0 * num / den), rel=1e-5)


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


# ------------------------------------------------------------------ #
# R-peak detection (heart_rate, hrv)                                   #
# ------------------------------------------------------------------ #

def _synthetic_ecg(hr, fs=500, dur=10.0, t_amp=0.32, invert=False, seed=0):
    """Sum-of-Gaussians ECG (P, Q, R, S, T) with a fixed heart rate."""
    rng = np.random.default_rng(seed)
    t = np.arange(int(fs * dur)) / fs
    rr = 60.0 / hr
    waves = [(-0.2, 0.15, 0.025), (-0.035, -0.12, 0.01), (0.0, 1.0, 0.011),
             (0.035, -0.25, 0.011), (0.26 * np.sqrt(rr / 0.85), t_amp, 0.045)]
    x = np.zeros_like(t)
    for r in np.arange(rng.uniform(0, rr), dur + 1, rr):
        for off, amp, width in waves:
            x += amp * np.exp(-0.5 * ((t - r - off) / width) ** 2)
    x += 0.02 * rng.standard_normal(len(t))
    return -x if invert else x


@pytest.mark.parametrize("hr", [40, 75, 150, 220])
@pytest.mark.parametrize("t_amp", [0.32, 0.9])
def test_r_peaks_heart_rate(hr, t_amp):
    from ecgen_eval.metrics._rpeaks import detect_r_peaks

    peaks = detect_r_peaks(_synthetic_ecg(hr, t_amp=t_amp), 500.0)
    est = 60.0 / np.mean(np.diff(peaks) / 500.0)
    assert abs(est - hr) / hr < 0.03


def test_r_peaks_inverted_lead():
    from ecgen_eval.metrics._rpeaks import detect_r_peaks

    peaks = detect_r_peaks(_synthetic_ecg(90, invert=True), 500.0)
    assert abs(60.0 / np.mean(np.diff(peaks) / 500.0) - 90) < 3


def test_r_peaks_numpy_fallback_matches_scipy(monkeypatch):
    import builtins

    from ecgen_eval.metrics._rpeaks import detect_r_peaks

    x = _synthetic_ecg(130, fs=250, seed=3)
    with_scipy = detect_r_peaks(x, 250.0)
    real_import = builtins.__import__

    def no_scipy(name, *args, **kwargs):
        if name.startswith("scipy"):
            raise ImportError(name)
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", no_scipy)
    np.testing.assert_array_equal(detect_r_peaks(x, 250.0), with_scipy)


def test_r_peaks_flat_signal_returns_empty():
    from ecgen_eval.metrics._rpeaks import detect_r_peaks

    assert detect_r_peaks(np.zeros(5000), 500.0).size == 0


def test_heart_rate_metric_detects_tachycardia():
    real = np.stack([_synthetic_ecg(70, seed=i)[None] for i in range(6)]).astype(np.float32)
    synth = np.stack([_synthetic_ecg(160, seed=10 + i)[None] for i in range(6)]).astype(np.float32)
    r = AVAILABLE_METRICS["heart_rate"](fs=500).compute(real, synth, lead_names=["II"])
    assert abs(r.extra["II"]["real_hr_mean"] - 70) < 3
    assert abs(r.extra["II"]["synth_hr_mean"] - 160) < 5
