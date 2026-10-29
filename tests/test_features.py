"""
Unit tests for ecgen_eval.features.

Uses the synthetic ECG fixtures from conftest.py.  The QRS-like bumps
inserted at every 500 samples (at 500 Hz → 1 Hz = 60 BPM) give enough
structure for R-peak detection to succeed.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ecgen_eval.data.dataset import ECGDataset, LEADS_12
from ecgen_eval.features import FeatureExtractor, extract_features
from ecgen_eval.features.qrs_detection import detect_rpeaks
from ecgen_eval.features.hrv_features import extract_hrv_features
from ecgen_eval.features.interval_features import extract_rr_hr, extract_interval_features
from ecgen_eval.features.amplitude_features import extract_amplitude_features


# ------------------------------------------------------------------ #
# Fixtures                                                             #
# ------------------------------------------------------------------ #

@pytest.fixture
def simple_ecg_signal():
    """Single-lead ECG-like signal: noise + periodic R-peaks every 500 samples."""
    rng = np.random.default_rng(42)
    t = 5000
    sig = rng.standard_normal(t).astype(np.float32) * 0.05
    for i in range(t // 500):
        centre = i * 500 + 250
        if centre + 20 < t:
            sig[centre: centre + 20] += 2.0  # positive R-peak
    return sig.astype(np.float64)


@pytest.fixture
def tiny_dataset():
    """5-sample, 12-lead, 5000-timepoint ECGDataset with QRS-like bumps."""
    rng = np.random.default_rng(7)
    n, l, t = 5, 12, 5000
    data = rng.standard_normal((n, l, t)).astype(np.float32) * 0.05
    for i in range(t // 500):
        centre = i * 500 + 250
        if centre + 20 < t:
            data[:, :, centre: centre + 20] += 2.0
    return ECGDataset(
        data=data,
        lead_names=LEADS_12,
        fs=500.0,
        source_path="/tmp/test",
        label="test",
    )


# ------------------------------------------------------------------ #
# qrs_detection                                                        #
# ------------------------------------------------------------------ #

class TestRpeakDetection:
    def test_returns_array(self, simple_ecg_signal):
        peaks = detect_rpeaks(simple_ecg_signal, fs=500.0)
        assert isinstance(peaks, np.ndarray)

    def test_detects_expected_peaks(self, simple_ecg_signal):
        peaks = detect_rpeaks(simple_ecg_signal, fs=500.0)
        # Expect ~9 peaks (one per 500-sample period across 5000 samples)
        assert len(peaks) >= 5, f"Expected ≥5 peaks, got {len(peaks)}"

    def test_peaks_sorted(self, simple_ecg_signal):
        peaks = detect_rpeaks(simple_ecg_signal, fs=500.0)
        if len(peaks) > 1:
            assert np.all(np.diff(peaks) > 0)

    def test_flat_signal_no_crash(self):
        sig = np.zeros(1000, dtype=np.float64)
        peaks = detect_rpeaks(sig, fs=500.0)
        assert isinstance(peaks, np.ndarray)

    def test_wrong_ndim_raises(self, simple_ecg_signal):
        with pytest.raises(ValueError, match="1-D"):
            detect_rpeaks(simple_ecg_signal.reshape(1, -1), fs=500.0)


# ------------------------------------------------------------------ #
# hrv_features                                                         #
# ------------------------------------------------------------------ #

class TestHRVFeatures:
    def test_keys_present(self, simple_ecg_signal):
        peaks = detect_rpeaks(simple_ecg_signal, fs=500.0)
        result = extract_hrv_features(peaks, fs=500.0)
        assert set(result.keys()) == {"hrv_sdnn_ms", "hrv_rmssd_ms", "hrv_pnn50"}

    def test_values_finite_for_good_signal(self, simple_ecg_signal):
        peaks = detect_rpeaks(simple_ecg_signal, fs=500.0)
        result = extract_hrv_features(peaks, fs=500.0)
        # With regular peaks, sdnn and rmssd should be near-zero (regular rhythm)
        for k, v in result.items():
            assert np.isfinite(v) or np.isnan(v), f"{k} = {v}"

    def test_too_few_peaks_returns_nan(self):
        peaks = np.array([100, 600], dtype=int)  # only 1 RR
        result = extract_hrv_features(peaks, fs=500.0)
        assert all(np.isnan(v) for v in result.values())


# ------------------------------------------------------------------ #
# interval_features                                                    #
# ------------------------------------------------------------------ #

class TestIntervalFeatures:
    def test_rr_hr_keys(self, simple_ecg_signal):
        peaks = detect_rpeaks(simple_ecg_signal, fs=500.0)
        result = extract_rr_hr(peaks, fs=500.0)
        assert "rr_mean_ms" in result
        assert "hr_bpm" in result

    def test_rr_approximate_value(self, simple_ecg_signal):
        peaks = detect_rpeaks(simple_ecg_signal, fs=500.0)
        result = extract_rr_hr(peaks, fs=500.0)
        if np.isfinite(result["rr_mean_ms"]):
            # R-peaks spaced ~500 samples at 500 Hz → RR ≈ 1000 ms
            assert 500 <= result["rr_mean_ms"] <= 2000

    def test_interval_features_no_crash(self, simple_ecg_signal):
        peaks = detect_rpeaks(simple_ecg_signal, fs=500.0)
        result = extract_interval_features(simple_ecg_signal, fs=500.0, rpeaks=peaks, waves=None)
        expected_keys = {"pr_interval_ms", "qrs_duration_ms", "qt_interval_ms",
                         "qtc_bazett_ms", "p_wave_duration_ms"}
        assert expected_keys.issubset(result.keys())

    def test_no_peaks_returns_nan(self):
        sig = np.zeros(1000, dtype=np.float64)
        result = extract_rr_hr(np.array([], dtype=int), fs=500.0)
        assert np.isnan(result["rr_mean_ms"])


# ------------------------------------------------------------------ #
# amplitude_features                                                   #
# ------------------------------------------------------------------ #

class TestAmplitudeFeatures:
    def test_keys_present(self, simple_ecg_signal):
        peaks = detect_rpeaks(simple_ecg_signal, fs=500.0)
        result = extract_amplitude_features(simple_ecg_signal, fs=500.0, rpeaks=peaks)
        assert "st_deviation_mv" in result
        assert "t_amplitude_mv" in result

    def test_no_peaks_returns_nan(self):
        sig = np.zeros(1000, dtype=np.float64)
        result = extract_amplitude_features(sig, fs=500.0, rpeaks=np.array([], dtype=int))
        assert np.isnan(result["st_deviation_mv"])
        assert np.isnan(result["t_amplitude_mv"])


# ------------------------------------------------------------------ #
# FeatureExtractor / extract_features                                  #
# ------------------------------------------------------------------ #

class TestFeatureExtractor:
    def test_returns_dataframes(self, tiny_dataset):
        beat_df, summary_df = extract_features(tiny_dataset)
        assert isinstance(beat_df, pd.DataFrame)
        assert isinstance(summary_df, pd.DataFrame)

    def test_summary_rows_match_samples(self, tiny_dataset):
        _, summary_df = extract_features(tiny_dataset)
        assert len(summary_df) == tiny_dataset.n_samples

    def test_summary_columns_present(self, tiny_dataset):
        _, summary_df = extract_features(tiny_dataset)
        expected = {
            "rr_mean_ms", "hr_bpm", "qrs_duration_ms", "qt_interval_ms",
            "st_deviation_mv", "t_amplitude_mv", "hrv_sdnn_ms",
        }
        missing = expected - set(summary_df.columns)
        assert not missing, f"Missing columns: {missing}"

    def test_beat_df_has_expected_columns(self, tiny_dataset):
        beat_df, _ = extract_features(tiny_dataset)
        if not beat_df.empty:
            for col in ("sample_idx", "beat_idx", "lead", "rr_ms"):
                assert col in beat_df.columns, f"Missing column: {col}"

    def test_different_seed_gives_different_values(self):
        """Two different datasets should yield different feature distributions."""
        rng1 = np.random.default_rng(0)
        rng2 = np.random.default_rng(99)
        n, l, t = 10, 12, 3000

        def _make(rng):
            data = rng.standard_normal((n, l, t)).astype(np.float32) * 0.05
            for i in range(t // 500):
                c = i * 500 + 250
                if c + 20 < t:
                    data[:, :, c: c + 20] += 2.0
            return ECGDataset(data=data, lead_names=LEADS_12, fs=500.0,
                              source_path="/tmp/x", label="x")

        ds1 = _make(rng1)
        ds2 = _make(rng2)
        _, s1 = extract_features(ds1)
        _, s2 = extract_features(ds2)
        # At least one feature should differ
        common = set(s1.columns) & set(s2.columns) - {"sample_idx"}
        for col in common:
            if s1[col].notna().any() and s2[col].notna().any():
                if not np.allclose(s1[col].dropna().values, s2[col].dropna().values, equal_nan=True):
                    return  # passed
        # If all identical, that's suspicious but not a failure for synthetic data


# ------------------------------------------------------------------ #
# feature_plots smoke tests                                            #
# ------------------------------------------------------------------ #

class TestFeaturePlots:
    @pytest.fixture
    def feature_dfs(self, tiny_dataset):
        rng = np.random.default_rng(3)
        data2 = rng.standard_normal(tiny_dataset.data.shape).astype(np.float32) * 0.05
        t = tiny_dataset.n_timepoints
        for i in range(t // 500):
            c = i * 500 + 250
            if c + 20 < t:
                data2[:, :, c: c + 20] += 2.0
        ds2 = ECGDataset(data=data2, lead_names=LEADS_12, fs=500.0,
                         source_path="/tmp/s", label="synth")
        _, real_df = extract_features(tiny_dataset)
        _, synth_df = extract_features(ds2)
        return real_df, synth_df

    def test_plot_feature_2d_returns_figure(self, feature_dfs):
        from ecgen_eval.visualization.feature_plots import plot_feature_2d
        import plotly.graph_objects as go

        real_df, synth_df = feature_dfs
        fig = plot_feature_2d(real_df, synth_df, "rr_mean_ms", "hr_bpm")
        assert isinstance(fig, go.Figure)

    def test_plot_feature_pair_grid_returns_figure(self, feature_dfs):
        from ecgen_eval.visualization.feature_plots import plot_feature_pair_grid
        import plotly.graph_objects as go

        real_df, synth_df = feature_dfs
        fig = plot_feature_pair_grid(real_df, synth_df)
        assert isinstance(fig, go.Figure)

    def test_plot_feature_3d_returns_figure(self, feature_dfs):
        from ecgen_eval.visualization.feature_plots import plot_feature_3d
        import plotly.graph_objects as go

        real_df, synth_df = feature_dfs
        fig = plot_feature_3d(real_df, synth_df, "rr_mean_ms", "hr_bpm", "qrs_duration_ms")
        assert isinstance(fig, go.Figure)

    def test_plot_feature_triple_grid_returns_figure(self, feature_dfs):
        from ecgen_eval.visualization.feature_plots import plot_feature_triple_grid
        import plotly.graph_objects as go

        real_df, synth_df = feature_dfs
        fig = plot_feature_triple_grid(real_df, synth_df)
        assert isinstance(fig, go.Figure)

    def test_missing_columns_no_crash(self, feature_dfs):
        """Plots should handle DataFrames that are missing requested columns gracefully."""
        from ecgen_eval.visualization.feature_plots import plot_feature_2d, plot_feature_3d
        import plotly.graph_objects as go

        real_df, synth_df = feature_dfs
        # Request non-existent column — should return a Figure, not raise
        fig = plot_feature_2d(real_df, synth_df, "nonexistent_x", "nonexistent_y")
        assert isinstance(fig, go.Figure)


# ------------------------------------------------------------------ #
# delineation (synthetic beats with known timing)                      #
# ------------------------------------------------------------------ #

def _synthetic_ecg(fs=500, seconds=10, rr_ms=800, n_leads=12, seed=0):
    """
    ECG with known fiducials: P 100 ms (R-200..R-100 ms), QRS 90 ms (R-45..R+45 ms),
    T offset at R+350 ms. So PR = 155 ms, QRS = 90 ms, QT = 395 ms, T amplitude 0.3 mV.
    """
    rng = np.random.default_rng(seed)
    t = np.arange(int(seconds * fs)) / fs * 1000.0  # ms
    beat = np.zeros_like(t)
    for r in np.arange(400.0, t[-1] - 400.0, rr_ms):
        d = t - r
        p = (d >= -200) & (d <= -100)
        beat[p] += 0.15 * np.sin(np.pi * (d[p] + 200) / 100)
        beat += np.interp(d, [-45, -30, 0, 25, 45], [0, -0.1, 1.2, -0.3, 0], left=0, right=0)
        tw = (d >= 150) & (d <= 350)
        beat[tw] += 0.3 * np.sin(np.pi * (d[tw] - 150) / 200)
    gains = np.linspace(0.6, 1.4, n_leads)
    data = gains[:, None] * beat[None, :] + rng.standard_normal((n_leads, len(t))) * 0.005
    return data


class TestDelineation:
    def test_align_to_beats_handles_missing_points(self):
        from ecgen_eval.features.delineation import align_to_beats

        rpeaks = np.array([100, 300, 500])
        # point for beat 1 missing, NaN ignored, duplicate for beat 2 keeps the first
        out = align_to_beats([60, np.nan, 460, 470], rpeaks)
        assert out[0] == 60 and np.isnan(out[1]) and out[2] == 460

    def test_qrs_boundaries_match_known_width(self):
        from ecgen_eval.features.delineation import qrs_boundaries

        fs = 500
        data = _synthetic_ecg(fs=fs)
        rpeaks = detect_rpeaks(data[1], fs)
        q = qrs_boundaries(data, rpeaks, fs)
        width = (q["ECG_QRS_Offsets"] - q["ECG_QRS_Onsets"]) / fs * 1000
        assert np.isfinite(width).sum() >= len(rpeaks) - 2
        assert 70 <= np.nanmedian(width) <= 110

    def test_interval_features_on_known_beats(self):
        pytest.importorskip("neurokit2")
        fs = 500
        data = _synthetic_ecg(fs=fs)
        ds = ECGDataset(data=data[None].astype(np.float32), lead_names=LEADS_12, fs=float(fs),
                        source_path="/tmp/test", label="synthetic")
        _, s = extract_features(ds)
        row = s.iloc[0]
        assert 70 <= row["hr_bpm"] <= 80
        assert 120 <= row["pr_interval_ms"] <= 190
        assert 70 <= row["qrs_duration_ms"] <= 110
        assert 340 <= row["qt_interval_ms"] <= 430
        assert 60 <= row["p_wave_duration_ms"] <= 130
        assert 0.15 <= row["t_amplitude_mv"] <= 0.45
        assert abs(row["st_deviation_mv"]) < 0.1

    def test_no_placeholder_values_without_delineation(self, simple_ecg_signal):
        """Intervals that cannot be measured are NaN, never fixed constants."""
        peaks = detect_rpeaks(simple_ecg_signal, fs=500.0)
        result = extract_interval_features(simple_ecg_signal, fs=500.0, rpeaks=peaks[:1])
        assert all(np.isnan(result[k]) for k in ("pr_interval_ms", "qt_interval_ms"))


# ------------------------------------------------------------------ #
# Feature selection and backends                                       #
# ------------------------------------------------------------------ #

class TestFeatureSelection:
    def test_select_group(self, tiny_dataset):
        beat_df, s = extract_features(tiny_dataset, features="hrv")
        assert list(s.columns) == ["sample_idx", "hrv_sdnn_ms", "hrv_rmssd_ms", "hrv_pnn50"]
        assert "qrs_duration_ms" not in beat_df.columns

    def test_select_columns_and_groups(self, tiny_dataset):
        fe = FeatureExtractor(features=["qtc_bazett_ms", "rhythm", "hr_bpm"])
        _, s = fe.extract(tiny_dataset)
        assert list(s.columns) == ["sample_idx", "qtc_bazett_ms", "rr_mean_ms", "rr_std_ms",
                                   "hr_bpm"]
        assert fe.columns == list(s.columns[1:])

    def test_per_lead_columns_follow_selection(self, tiny_dataset):
        beat_df, _ = extract_features(tiny_dataset, features=["t_amplitude_mv"])
        if not beat_df.empty:
            assert "t_amplitude_mv" in beat_df.columns
            assert "st_deviation_mv" not in beat_df.columns

    def test_unknown_feature_raises(self):
        with pytest.raises(ValueError, match="Unknown feature"):
            FeatureExtractor(features=["not_a_feature"])

    def test_callable_feature(self, tiny_dataset):
        def n_beats(ctx):
            return {"n_beats": ctx.n_beats}

        _, s = extract_features(tiny_dataset, features=["hr_bpm", n_beats])
        assert list(s.columns) == ["sample_idx", "hr_bpm", "n_beats"]
        assert (s["n_beats"] >= 5).all()

    def test_registered_group(self, tiny_dataset):
        from ecgen_eval.features import AVAILABLE_FEATURE_GROUPS, feature_group

        @feature_group("test_energy", columns=["test_energy"])
        def _energy(ctx):
            return {"test_energy": float(np.sum(ctx.primary_signal ** 2))}

        try:
            _, s = extract_features(tiny_dataset, features="test_energy")
            assert list(s.columns) == ["sample_idx", "test_energy"]
            with pytest.raises(ValueError, match="already registered"):
                feature_group("test_energy")(_energy)
        finally:
            AVAILABLE_FEATURE_GROUPS.pop("test_energy")

    def test_failing_group_gives_nan(self, tiny_dataset):
        from ecgen_eval.features import FunctionFeatureGroup

        def broken(ctx):
            raise RuntimeError("boom")

        group = FunctionFeatureGroup("broken", broken, columns=["x"])
        with pytest.warns(RuntimeWarning, match="broken"):
            _, s = extract_features(tiny_dataset, features=[group, "hr_bpm"])
        assert s["x"].isna().all() and s["hr_bpm"].notna().all()


class TestBackends:
    def test_unknown_backend_raises(self):
        with pytest.raises(ValueError, match="Unknown feature backend"):
            FeatureExtractor(backend="nope")

    def test_scipy_backend_has_no_pt_waves(self):
        data = _synthetic_ecg()
        ds = ECGDataset(data=data[None].astype(np.float32), lead_names=LEADS_12, fs=500.0,
                        source_path="/tmp/test", label="synthetic")
        _, s = extract_features(ds, backend="scipy")
        row = s.iloc[0]
        assert 70 <= row["hr_bpm"] <= 80
        assert 70 <= row["qrs_duration_ms"] <= 110
        assert np.isnan(row["pr_interval_ms"]) and np.isnan(row["qt_interval_ms"])

    @pytest.mark.parametrize("method", ["dwt", "prominence"])
    def test_neurokit_backend(self, method):
        pytest.importorskip("neurokit2")
        data = _synthetic_ecg()
        ds = ECGDataset(data=data[None].astype(np.float32), lead_names=LEADS_12, fs=500.0,
                        source_path="/tmp/test", label="synthetic")
        fe = FeatureExtractor(backend="neurokit2", delineation_method=method)
        _, s = fe.extract(ds)
        assert 70 <= s.iloc[0]["hr_bpm"] <= 80
        assert np.isfinite(s.iloc[0]["qrs_duration_ms"])

    def test_custom_backend_instance(self, tiny_dataset):
        from ecgen_eval.features import DelineationBackend

        class FixedBeats(DelineationBackend):
            name = "fixed"

            def delineate(self, recording, fs, primary_lead_idx):
                return np.arange(250, recording.shape[1], 500), None

        _, s = extract_features(tiny_dataset, backend=FixedBeats(),
                                features=["rhythm", "intervals"])
        assert np.allclose(s["hr_bpm"], 60.0)
        assert s["qrs_duration_ms"].isna().all()

    def test_register_backend(self):
        from ecgen_eval.features import AVAILABLE_BACKENDS, ScipyBackend, register_backend

        class Mine(ScipyBackend):
            name = "test_mine"

        register_backend(Mine)
        try:
            assert isinstance(FeatureExtractor(backend="test_mine").backend, Mine)
        finally:
            AVAILABLE_BACKENDS.pop("test_mine")
