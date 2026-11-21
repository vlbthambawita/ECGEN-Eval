"""Tests for the fidelity metrics added from the literature review (issue #96)."""

import numpy as np
import pytest

from ecgen_eval.metrics import (
    AVAILABLE_METRICS,
    AmplitudeJSMetric,
    C2STMetric,
    CosineMetric,
    CurveFrechetMetric,
    EuclideanMetric,
    KSTestMetric,
    MAEMetric,
    MSEMetric,
    PearsonMetric,
    RMSEMetric,
)
from ecgen_eval.metrics.base import MetricResult
from ecgen_eval.metrics._stats import adjust_pvalues, cohens_d, ks_2samp, ks_statistic
from ecgen_eval.metrics.curve_frechet import discrete_frechet, discrete_frechet_reference

PAIRWISE = [MSEMetric, RMSEMetric, EuclideanMetric, PearsonMetric, CosineMetric, CurveFrechetMetric]
NEW_KEYS = ["mse", "rmse", "pearson", "cosine", "euclidean", "curve_frechet",
            "js_div", "ks_test", "c2st"]


def _rand(n, leads=3, t=200, seed=0):
    return np.random.default_rng(seed).standard_normal((n, leads, t))


# ------------------------------------------------------------------ #
# Shared behaviour                                                     #
# ------------------------------------------------------------------ #

@pytest.mark.parametrize("key", NEW_KEYS)
def test_basic_contract(key, real_ecg, synth_ecg):
    metric = AVAILABLE_METRICS[key]()          # constructor takes no arguments
    assert metric.name == key and metric.description and metric.reference
    result = metric.compute(real_ecg, synth_ecg)
    assert isinstance(result, MetricResult) and result.metric_name == key
    assert np.isfinite(result.score)
    assert len(result.per_lead_scores) == 12
    assert result.higher_is_better == (key in {"pearson", "cosine"})
    assert result.score == pytest.approx(np.mean(list(result.per_lead_scores.values())))
    again = AVAILABLE_METRICS[key]().compute(real_ecg, synth_ecg)
    assert again.score == result.score          # fixed seed -> reproducible


@pytest.mark.parametrize("key", NEW_KEYS)
def test_lead_mismatch_raises(key, real_ecg):
    with pytest.raises(ValueError):
        AVAILABLE_METRICS[key]().compute(real_ecg, np.zeros((10, 8, 5000), dtype=np.float32))


@pytest.mark.parametrize("cls", PAIRWISE)
def test_pairwise_identical_data_is_best(cls):
    x = _rand(20)
    best = 1.0 if cls.higher_is_better else 0.0
    assert cls().compute(x, x).score == pytest.approx(best, abs=1e-9)
    assert cls(pairing="paired").compute(x, x).score == pytest.approx(best, abs=1e-9)


@pytest.mark.parametrize("cls", PAIRWISE)
def test_pairwise_extra_and_baseline(cls):
    r, s = _rand(30, seed=1), _rand(20, seed=2)
    res = cls().compute(r, s, lead_names=["I", "II", "V1"])
    assert list(res.per_lead_scores) == ["I", "II", "V1"]
    assert res.extra["pairing"] == "nn"
    assert np.isfinite(res.extra["real_vs_real"])
    assert set(res.extra["per_lead_real_vs_real"]) == {"I", "II", "V1"}
    n_pairs = 30
    assert len(res.extra["per_lead_all_values"]["I"]) == n_pairs
    off = cls(baseline=False).compute(r, s)
    assert "real_vs_real" not in off.extra
    assert off.score == res.score             # the baseline never changes the score


@pytest.mark.parametrize("cls", PAIRWISE)
def test_pairwise_modes(cls):
    r, s = _rand(16, seed=3), _rand(16, seed=4)
    for pairing in ("nn", "paired", "mean"):
        res = cls(pairing=pairing).compute(r, s)
        assert np.isfinite(res.score) and res.extra["pairing"] == pairing
    with pytest.raises(ValueError, match="same number"):
        cls(pairing="paired").compute(r, s[:10])
    with pytest.raises(ValueError):
        cls(pairing="closest")


@pytest.mark.parametrize("cls", PAIRWISE)
def test_length_mismatch_raises(cls):
    with pytest.raises(ValueError, match="length"):
        cls().compute(_rand(5, t=100), _rand(5, t=120))


# ------------------------------------------------------------------ #
# MSE / RMSE / Euclidean                                               #
# ------------------------------------------------------------------ #

def test_rmse_equals_mae_extra(real_ecg, synth_ecg):
    rmse = RMSEMetric().compute(real_ecg, synth_ecg)
    mae = MAEMetric().compute(real_ecg, synth_ecg)
    assert rmse.score == pytest.approx(mae.extra["rmse"], rel=1e-6)
    for lead, value in mae.extra["per_lead_rmse"].items():
        assert rmse.per_lead_scores[lead] == pytest.approx(value, rel=1e-6)


def test_paired_constant_offset():
    r = _rand(12, t=250)
    c = 0.3
    assert MSEMetric(pairing="paired").compute(r, r + c).score == pytest.approx(c ** 2)
    assert RMSEMetric(pairing="paired").compute(r, r + c).score == pytest.approx(c)
    eu = EuclideanMetric(pairing="paired").compute(r, r + c)
    assert eu.score == pytest.approx(c * np.sqrt(250))
    assert eu.extra["length_normalised"] == pytest.approx(c)
    assert eu.extra["n_timepoints"] == 250


def test_mse_and_rmse_report_each_other():
    r, s = _rand(15, seed=5), _rand(15, seed=6)
    mse, rmse = MSEMetric().compute(r, s), RMSEMetric().compute(r, s)
    assert mse.extra["rmse"] == pytest.approx(rmse.score)
    assert rmse.extra["mse"] == pytest.approx(mse.score)
    assert 0 < rmse.extra["nrmse"] < 1


def test_euclidean_length_normalised_equals_rmse():
    r, s = _rand(15, seed=7), _rand(15, seed=8)
    eu, rmse = EuclideanMetric().compute(r, s), RMSEMetric().compute(r, s)
    assert eu.extra["length_normalised"] == pytest.approx(rmse.score)


def test_zscore_makes_mse_scale_invariant():
    r, s = _rand(15, seed=9), _rand(15, seed=10)
    a = MSEMetric(normalize="zscore", pairing="paired").compute(r, s).score
    b = MSEMetric(normalize="zscore", pairing="paired").compute(r, 7.0 * s + 2.0).score
    assert a == pytest.approx(b)
    assert MSEMetric(normalize="minmax").compute(r, s).extra["normalize"] == "minmax"
    with pytest.raises(ValueError):
        MSEMetric(normalize="robust")


# ------------------------------------------------------------------ #
# Pearson / cosine                                                     #
# ------------------------------------------------------------------ #

def test_pearson_matches_numpy_and_bounds():
    r, s = _rand(10, leads=1, seed=11), _rand(10, leads=1, seed=12)
    res = PearsonMetric(pairing="paired").compute(r, s)
    expected = np.mean([np.corrcoef(r[i, 0], s[i, 0])[0, 1] for i in range(10)])
    assert res.score == pytest.approx(expected)
    assert PearsonMetric(pairing="paired").compute(r, -r).score == pytest.approx(-1.0)


def test_pearson_ignores_gain_and_offset_cosine_does_not():
    r = _rand(10, seed=13)
    shifted = 2.5 * r + 4.0
    assert PearsonMetric(pairing="paired").compute(r, shifted).score == pytest.approx(1.0)
    cos = CosineMetric(pairing="paired")
    assert cos.compute(r, 2.5 * r).score == pytest.approx(1.0)       # gain: no effect
    assert cos.compute(r, shifted).score < 0.9                       # offset: changes it
    assert cos.compute(r, -r).score == pytest.approx(-1.0)


def test_cosine_equals_pearson_for_zero_mean_signals():
    r, s = _rand(10, seed=14), _rand(10, seed=15)
    r -= r.mean(axis=2, keepdims=True)
    s -= s.mean(axis=2, keepdims=True)
    assert CosineMetric(pairing="paired").compute(r, s).score == pytest.approx(
        PearsonMetric(pairing="paired").compute(r, s).score)


def test_pearson_nn_picks_best_correlated_signal():
    rng = np.random.default_rng(16)
    r = rng.standard_normal((1, 1, 300))
    synth = np.concatenate([r * 50.0 + 3.0, r + 0.5 * rng.standard_normal((1, 1, 300))])
    # Row 0 is far in Euclidean terms but perfectly correlated.
    assert PearsonMetric(baseline=False).compute(r, synth).score == pytest.approx(1.0)


def test_flat_signals_are_skipped_not_fatal():
    r = _rand(6, seed=17)
    s = _rand(6, seed=18)
    s[:, 1, :] = 0.0                      # a flat synthetic lead
    for cls in (PearsonMetric, CosineMetric):
        res = cls(pairing="paired", baseline=False).compute(r, s)
        assert res.extra["n_skipped"] == 6
        assert np.isnan(res.per_lead_scores["L2"])
        assert np.isfinite(res.score)     # mean over the remaining leads


def test_pearson_cross_correlation_recovers_shift():
    fs, shift = 250.0, 5                  # 5 samples = 20 ms late
    r = _rand(4, leads=1, t=500, seed=42)   # broadband: a sharp correlation peak
    s = np.roll(r, shift, axis=2)
    res = PearsonMetric(pairing="paired", max_lag_ms=60, fs=fs, baseline=False).compute(r, s)
    assert res.extra["best_lag_ms"] == pytest.approx(1000 * shift / fs)
    assert res.extra["xcorr_max"] > res.score
    assert "xcorr_max" not in PearsonMetric().compute(r, s).extra


# ------------------------------------------------------------------ #
# Curve Fréchet                                                        #
# ------------------------------------------------------------------ #

def test_discrete_frechet_hand_example():
    # Best coupling walks (1,1) (2,2) (3,3): gaps 1, 0, 1 -> distance 1.
    assert discrete_frechet([0, 1, 2], [1, 1, 1]) == pytest.approx(1.0)
    assert discrete_frechet([0.0], [3.0]) == pytest.approx(3.0)
    assert discrete_frechet([0, 5, 0], [0, 0]) == pytest.approx(5.0)   # the peak must be visited


def test_discrete_frechet_matches_reference_and_properties():
    rng = np.random.default_rng(19)
    for _ in range(10):
        p = rng.standard_normal(rng.integers(1, 25))
        q = rng.standard_normal(rng.integers(1, 25))
        for tw in (0.0, 3.0):
            ref = discrete_frechet_reference(p, q, tw, 0.1)
            assert discrete_frechet(p, q, tw, 0.1) == pytest.approx(ref)
            assert discrete_frechet(q, p, tw, 0.1) == pytest.approx(ref)   # symmetric
    P, Q = rng.standard_normal((6, 30)), rng.standard_normal((6, 30))
    batch = discrete_frechet(P, Q)
    assert batch.shape == (6,)
    assert np.allclose(batch, [discrete_frechet_reference(p, q) for p, q in zip(P, Q)])
    assert np.all(batch <= np.max(np.abs(P - Q), axis=1) + 1e-12)   # diagonal coupling bound
    assert np.allclose(discrete_frechet(P, P + 0.4), 0.4)


def test_curve_frechet_time_weight_penalises_shifts():
    x = np.zeros((4, 1, 400))
    x[:, 0, 100:110] = 1.0
    shifted = np.roll(x, 40, axis=2)
    free = CurveFrechetMetric(pairing="paired", max_len=400, baseline=False).compute(x, shifted)
    timed = CurveFrechetMetric(pairing="paired", max_len=400, time_weight=5.0, fs=100.0,
                               baseline=False).compute(x, shifted)
    assert free.score == pytest.approx(0.0)        # amplitude-only: a pure shift is free
    assert timed.score > 0.5


def test_curve_frechet_decimates_and_reports_it():
    res = CurveFrechetMetric(max_len=100, fs=500.0).compute(_rand(8, t=1000), _rand(8, t=1000, seed=1))
    assert res.extra["n_points"] == 100
    assert res.extra["effective_fs"] == pytest.approx(50.0)
    with pytest.raises(ValueError):
        CurveFrechetMetric(max_len=1)


# ------------------------------------------------------------------ #
# Amplitude JS / KL                                                    #
# ------------------------------------------------------------------ #

def test_js_div_identical_and_disjoint():
    r = _rand(30, seed=20)
    assert AmplitudeJSMetric().compute(r, r).score == pytest.approx(0.0, abs=1e-12)
    far = AmplitudeJSMetric().compute(r, r + 1000.0)
    assert far.score == pytest.approx(np.log(2), rel=1e-2)
    assert all(v == pytest.approx(1.0) for v in far.extra["per_lead_tail_mass"].values())


def test_js_div_monotone_in_gain_and_extras():
    r, s = _rand(40, seed=21), _rand(40, seed=22)
    scores = [AmplitudeJSMetric().compute(r, g * s).score for g in (1.0, 1.5, 2.0, 3.0)]
    assert scores == sorted(scores) and scores[0] < 0.01
    res = AmplitudeJSMetric(n_bins=40).compute(r, 2.0 * s)
    assert res.extra["kl_real_synth"] > 0 and res.extra["kl_synth_real"] > 0
    assert res.extra["kl_real_synth"] != pytest.approx(res.extra["kl_synth_real"])
    hist = res.extra["per_lead_hist_real"]["L1"]
    assert len(hist) == 42 and sum(hist) == pytest.approx(1.0)        # 40 bins + 2 tails
    assert len(res.extra["bin_edges"]["L1"]) == 41
    assert res.extra["per_lead_js_distance"]["L1"] == pytest.approx(
        np.sqrt(res.per_lead_scores["L1"]))


def test_js_div_ignores_temporal_order_and_constant_leads():
    r, s = _rand(20, seed=23), 1.3 * _rand(20, seed=24)
    shuffled = np.random.default_rng(0).permuted(s, axis=2)
    assert AmplitudeJSMetric().compute(r, shuffled).score == pytest.approx(
        AmplitudeJSMetric().compute(r, s).score)
    flat = np.zeros((5, 2, 50))
    assert AmplitudeJSMetric().compute(flat, flat).score == pytest.approx(0.0, abs=1e-12)


# ------------------------------------------------------------------ #
# KS test                                                              #
# ------------------------------------------------------------------ #

def test_ks_statistic_extremes_and_scipy_agreement():
    a = np.arange(50, dtype=float)
    assert ks_statistic(a, a) == 0.0
    assert ks_statistic(a, a + 1000) == 1.0
    assert np.isnan(ks_statistic(a, np.array([])))
    stats = pytest.importorskip("scipy.stats")
    rng = np.random.default_rng(25)
    for _ in range(5):
        x, y = rng.standard_normal(80), rng.standard_normal(120) + 0.3
        ref = stats.ks_2samp(x, y)
        d, p, method = ks_2samp(x, y)
        assert d == pytest.approx(ref.statistic)
        assert p == pytest.approx(ref.pvalue) and method == "scipy"


def test_ks_asymptotic_pvalue_is_close_to_scipy():
    stats = pytest.importorskip("scipy.stats")
    from ecgen_eval.metrics._stats import ks_pvalue_asymptotic

    rng = np.random.default_rng(26)
    x, y = rng.standard_normal(400), rng.standard_normal(500) + 0.1
    ref = stats.ks_2samp(x, y, method="asymp")
    assert ks_pvalue_asymptotic(ref.statistic, 400, 500) == pytest.approx(ref.pvalue, abs=0.02)
    assert ks_pvalue_asymptotic(0.0, 10, 10) == 1.0


def test_adjust_pvalues():
    p = np.array([0.01, 0.04, 0.03, np.nan])
    holm = adjust_pvalues(p, "holm")
    assert np.allclose(holm[:3], [0.03, 0.06, 0.06]) and np.isnan(holm[3])
    assert np.all(holm[:3] >= p[:3])
    assert np.allclose(adjust_pvalues(p, "bonferroni")[:3], [0.03, 0.12, 0.09])
    assert np.allclose(adjust_pvalues(p, "none")[:3], p[:3])
    with pytest.raises(ValueError):
        adjust_pvalues(p, "fdr")
    assert cohens_d(np.zeros(5), np.zeros(5)) == 0.0


def test_ks_test_metric():
    r, s = _rand(60, seed=27), _rand(45, seed=28)        # unequal sample sizes
    same = KSTestMetric().compute(r, r)
    assert same.score == 0.0 and same.extra["n_rejected"] == 0
    diff = KSTestMetric().compute(r, 2.0 * s)
    assert diff.score > 0.5
    assert diff.extra["per_feature_D"]["std"] == pytest.approx(1.0)
    assert diff.extra["n_tests"] == 21 and diff.extra["n_rejected"] > 0
    assert set(diff.extra["per_lead_feature_D"]["L1"]) == set(diff.extra["feature_names"])
    raw = diff.extra["per_lead_feature_p"]["L1"]
    adj = diff.extra["per_lead_feature_p_adjusted"]["L1"]
    assert all(adj[k] >= raw[k] - 1e-15 for k in raw)
    with pytest.raises(ValueError):
        KSTestMetric(correction="fdr")


def test_ks_test_works_without_scipy(monkeypatch):
    import builtins

    real_import = builtins.__import__

    def no_scipy(name, *args, **kwargs):
        if name.startswith("scipy"):
            raise ImportError("scipy disabled for this test")
        return real_import(name, *args, **kwargs)

    r, s = _rand(40, seed=29), 1.5 * _rand(40, seed=30)
    with_scipy = KSTestMetric().compute(r, s)
    monkeypatch.setattr(builtins, "__import__", no_scipy)
    without = KSTestMetric().compute(r, s)
    assert without.extra["p_method"] == "asymptotic"
    assert "per_lead_feature_mwu_p" not in without.extra
    assert without.score == pytest.approx(with_scipy.score)        # D never needs SciPy


# ------------------------------------------------------------------ #
# Classifier two-sample test                                           #
# ------------------------------------------------------------------ #

def test_c2st_same_distribution_scores_low():
    res = C2STMetric().compute(_rand(150, seed=31), _rand(150, seed=32))
    assert res.score < 0.1
    assert 0.35 < res.extra["all_leads"]["accuracy"] < 0.65


def test_c2st_identical_sets_score_zero():
    x = _rand(40, seed=33)
    assert C2STMetric().compute(x, x).score == 0.0      # below-chance accuracy is clipped


def test_c2st_detects_different_distribution():
    r, s = _rand(80, seed=34), 2.0 * _rand(60, seed=35)   # unequal N is balanced
    res = C2STMetric().compute(r, s)
    assert res.score > 0.4 and res.extra["auc"] > 0.9
    assert res.extra["n_per_class"] == 60
    assert res.extra["all_leads"]["p_above_chance"] < 1e-6
    assert res.extra["one_nn_loo_accuracy"] > 0.9
    top = max(res.extra["feature_importance"], key=res.extra["feature_importance"].get)
    assert top in {"std", "rms", "energy", "max_abs"}
    assert len(res.extra["per_lead_fold_accuracy"]["L1"]) == 5


@pytest.mark.parametrize("classifier", ["logreg", "rf", "knn"])
@pytest.mark.parametrize("features", ["handcrafted", "signal"])
def test_c2st_options_run(classifier, features):
    res = C2STMetric(classifier=classifier, features=features, n_splits=3).compute(
        _rand(24, leads=2, seed=36), 2.0 * _rand(24, leads=2, seed=37))
    assert 0.0 <= res.score <= 0.5
    assert res.extra["classifier"] == classifier and res.extra["features"] == features


def test_c2st_edge_cases():
    with pytest.warns(RuntimeWarning):
        tiny = C2STMetric().compute(_rand(3, seed=38), _rand(3, seed=39))
    assert np.isnan(tiny.score) and len(tiny.per_lead_scores) == 3
    small = C2STMetric().compute(_rand(4, seed=40), _rand(4, seed=41))   # folds reduced to 4
    assert small.extra["n_splits"] == 4
    with pytest.raises(ValueError):
        C2STMetric(classifier="svm")
    with pytest.raises(ValueError):
        C2STMetric(features="embedding")
