"""Tests for beat-band plots, embedding plots, feature statistics and their report/CLI wiring."""

import builtins

import numpy as np
import pandas as pd
import pytest
from click.testing import CliRunner

from ecgen_eval import cli
from ecgen_eval.data.dataset import ECGDataset
from ecgen_eval.features import compare_feature_distributions
from ecgen_eval.metrics import AVAILABLE_METRICS
from ecgen_eval.report.html_report import gallery_indices, generate_report
from ecgen_eval.visualization import (
    compute_embedding_2d,
    extract_aligned_beats,
    plot_amplitude_hist,
    plot_beat_bands,
    plot_ecg_comparison,
    plot_embedding_2d,
    plot_metric_violin,
)

FS = 250.0


def _ecg(hr, seed, fs=FS, dur=6.0, gain=1.0):
    """Sum-of-Gaussians ECG with a fixed heart rate."""
    rng = np.random.default_rng(seed)
    t = np.arange(int(fs * dur)) / fs
    rr = 60.0 / hr
    waves = [(-0.2, 0.15, 0.025), (-0.035, -0.12, 0.01), (0.0, 1.0, 0.011),
             (0.035, -0.25, 0.011), (0.25, 0.3, 0.045)]
    x = np.zeros_like(t)
    for r in np.arange(rng.uniform(0.1, rr), dur + 1, rr):
        for off, amp, width in waves:
            x += amp * np.exp(-0.5 * ((t - r - off) / width) ** 2)
    return gain * (x + 0.01 * rng.standard_normal(len(t)))


def _dataset(n, seed, label, gain=1.0, leads=("I", "II", "V1")):
    rng = np.random.default_rng(seed)
    data = np.stack([
        np.stack([_ecg(rng.uniform(55, 95), int(rng.integers(1e6)), gain=gain * (0.6 + 0.2 * li))
                  for li in range(len(leads))])
        for _ in range(n)
    ]).astype(np.float32)
    # Every lead of a recording shares the rhythm of lead 0 so that leads stay aligned.
    data[:, 1:, :] = data[:, :1, :] * np.array([0.8, 1.0])[None, :, None]
    return ECGDataset(data=data, lead_names=list(leads), fs=FS, source_path=None, label=label)


@pytest.fixture(scope="module")
def real():
    return _dataset(24, 0, "Real")


@pytest.fixture(scope="module")
def synth():
    return _dataset(20, 1, "Model A", gain=1.3)


# ------------------------------------------------------------------ #
# Beat bands                                                           #
# ------------------------------------------------------------------ #

def test_aligned_beats_have_r_peak_at_fixed_index(real):
    beats = extract_aligned_beats(real, "I", pre_ms=200, post_ms=400)
    r_index = int(round(200 * FS / 1000))
    assert beats.shape[1] == r_index + int(round(400 * FS / 1000))
    assert beats.shape[0] > 50
    peak = np.argmax(beats, axis=1)
    assert np.mean(np.abs(peak - r_index) <= 2) > 0.95      # no beat cut at an edge


def test_extract_aligned_beats_validation_and_cap(real):
    with pytest.raises(ValueError):
        extract_aligned_beats(real, "aVR")
    assert extract_aligned_beats(real, "II", max_beats=7).shape[0] == 7


def test_beat_bands_figure(real, synth):
    fig = plot_beat_bands(real, [synth])
    lines = [tr for tr in fig.data if tr.name]              # one median line per dataset+lead
    assert len(lines) == 2 * 3
    assert len(fig.data) == 3 * len(lines)                  # + upper and lower band edges
    assert "beats)" in lines[0].name
    one = plot_beat_bands(real, [synth], leads=["V1"], quantiles=(0.1, 0.5, 0.9))
    assert len([tr for tr in one.data if tr.name]) == 2
    assert min(one.data[2].x) == pytest.approx(-250.0, abs=5)


def test_beat_density_figure(real, synth):
    fig = plot_beat_bands(real, [synth], mode="density", leads=["I", "II"])
    assert len(fig.data) == 4 and all(tr.type == "heatmap" for tr in fig.data)
    z = np.array(fig.data[0].z)
    assert np.allclose(z.sum(axis=0), 1.0)                  # each time sample: shares sum to 1
    with pytest.raises(ValueError):
        plot_beat_bands(real, [synth], mode="violin")


def test_beat_bands_without_beats_gives_placeholder(real):
    flat = ECGDataset(data=np.zeros((4, 3, 1500), dtype=np.float32), lead_names=["I", "II", "V1"],
                      fs=FS, source_path=None, label="Flat")
    assert not plot_beat_bands(flat, [real]).data            # real set has no beats: message only
    fig = plot_beat_bands(real, [flat])                      # synthetic set has none: still drawn
    names = [tr.name for tr in fig.data if tr.name]
    assert len(names) == 3 and all(n.startswith("Real (") for n in names)


def test_show_r_peaks_adds_markers(real, synth):
    plain = plot_ecg_comparison(real, [synth], leads=["II"], add_calibration_pulse=False)
    marked = plot_ecg_comparison(real, [synth], leads=["II"], add_calibration_pulse=False,
                                 show_r_peaks=True)
    markers = [tr for tr in marked.data if tr.mode == "markers"]
    assert len(marked.data) == len(plain.data) + 2 and len(markers) == 2
    assert 4 <= len(markers[0].x) <= 10                      # 55-95 bpm over 6 s
    side = plot_ecg_comparison(real, [synth], leads=["II"], mode="sidebyside", show_r_peaks=True)
    assert len([tr for tr in side.data if tr.mode == "markers"]) == 2


# ------------------------------------------------------------------ #
# Embedding plots                                                      #
# ------------------------------------------------------------------ #

def test_pca_embedding_shapes_and_meta(real, synth):
    emb = compute_embedding_2d(real, [synth, synth], n_subsample=15)
    assert emb["real"].shape == (15, 2)
    assert list(emb["synth"]) == ["Model A", "Model A (2)"]     # duplicate labels are kept apart
    assert all(v.shape == (15, 2) for v in emb["synth"].values())
    meta = emb["meta"]
    assert meta["fit_on"] == "real" and meta["n_per_set"] == 15 and meta["method"] == "pca"
    assert "PC1" in meta["axis_labels"][0] and "%" in meta["axis_labels"][0]
    again = compute_embedding_2d(real, [synth, synth], n_subsample=15)
    assert np.array_equal(emb["real"], again["real"])       # deterministic


def test_fit_on_real_ignores_the_synthetic_set(real, synth):
    other = _dataset(20, 7, "Model B", gain=3.0)
    a = compute_embedding_2d(real, {"A": synth})
    b = compute_embedding_2d(real, {"B": other})
    assert np.allclose(a["real"], b["real"])                # real map does not move
    joint = compute_embedding_2d(real, {"B": other}, fit_on="joint")
    assert not np.allclose(a["real"], joint["real"])


@pytest.mark.parametrize("features", ["handcrafted", "signal"])
def test_embedding_feature_sets(real, synth, features):
    emb = compute_embedding_2d(real, [synth], features=features)
    assert emb["real"].shape == (20, 2) and emb["synth"]["Model A"].shape == (20, 2)
    assert np.isfinite(emb["real"]).all()


def test_tsne_is_reported_as_joint_and_clamps_perplexity(real, synth):
    emb = compute_embedding_2d(real, [synth], method="tsne", n_subsample=8, perplexity=500)
    assert emb["meta"]["fit_on"] == "joint"
    assert emb["real"].shape == (8, 2)


def test_embedding_from_arrays_and_dataframes():
    rng = np.random.default_rng(0)
    emb = compute_embedding_2d(rng.standard_normal((30, 6)), {"gen": rng.standard_normal((25, 6))})
    assert emb["real"].shape == (25, 2) and emb["meta"]["real_label"] == "Real"
    df_r = pd.DataFrame(rng.standard_normal((30, 4)), columns=list("abcd"))
    df_s = pd.DataFrame(rng.standard_normal((30, 4)), columns=list("abcd"))
    df_s.loc[:4, "a"] = np.nan                               # incomplete rows are dropped
    emb = compute_embedding_2d(df_r, {"gen": df_s}, features="clinical")
    assert emb["meta"]["n_dropped"]["gen"] == 5 and emb["meta"]["n_per_set"] == 25


def test_embedding_errors(real, synth, monkeypatch):
    with pytest.raises(ValueError):
        compute_embedding_2d(real, [synth], method="isomap")
    with pytest.raises(ValueError):
        compute_embedding_2d(real, [synth], fit_on="synthetic")
    with pytest.raises(ValueError):
        compute_embedding_2d(np.zeros((2, 3)), [np.zeros((2, 3))])
    real_import = builtins.__import__

    def no_umap(name, *args, **kwargs):
        if name == "umap":
            raise ImportError("no umap")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", no_umap)
    with pytest.raises(ImportError, match=r"ecgen-eval\[umap\]"):
        compute_embedding_2d(real, [synth], method="umap")


def test_umap_embedding(real, synth):
    pytest.importorskip("umap")
    emb = compute_embedding_2d(real, [synth], method="umap", n_neighbors=5)
    assert emb["real"].shape == (20, 2) and emb["meta"]["fit_on"] == "real"


def test_plot_embedding_2d(real, synth):
    fig = plot_embedding_2d(compute_embedding_2d(real, [synth]))
    assert [tr.type for tr in fig.data] == ["histogram2dcontour", "scatter", "scatter"]
    assert fig.data[2].name == "Model A"
    assert "fitted on real data only" in fig.layout.title.text


# ------------------------------------------------------------------ #
# Metric plots                                                         #
# ------------------------------------------------------------------ #

def test_amplitude_hist_and_violin(real, synth):
    res = AVAILABLE_METRICS["js_div"]().compute(real.data, synth.data, real.lead_names)
    fig = plot_amplitude_hist({"Model A": res})
    assert len(fig.data) == 2 * 3 and len(fig.data[0].x) == 102
    assert not plot_amplitude_hist({"x": AVAILABLE_METRICS["mmd"]().compute(real.data, synth.data)}).data
    pearson = AVAILABLE_METRICS["pearson"]().compute(real.data, synth.data, real.lead_names)
    violin = plot_metric_violin({"Model A": pearson}, "PEARSON")
    assert len(violin.data) == 3 and "Per-pair Value" in violin.layout.title.text


# ------------------------------------------------------------------ #
# Clinical feature statistics                                          #
# ------------------------------------------------------------------ #

def test_compare_feature_distributions():
    rng = np.random.default_rng(1)
    real_df = pd.DataFrame({"sample_idx": np.arange(200), "hr_bpm": rng.normal(70, 8, 200),
                            "qrs_duration_ms": rng.normal(95, 10, 200)})
    synth_df = pd.DataFrame({"sample_idx": np.arange(150), "hr_bpm": rng.normal(70, 8, 150),
                             "qrs_duration_ms": rng.normal(130, 10, 150)})
    synth_df.loc[:9, "hr_bpm"] = np.nan
    out = compare_feature_distributions(real_df, synth_df).set_index("feature")
    assert list(out.index) == ["hr_bpm", "qrs_duration_ms"]           # sample_idx is skipped
    assert out.loc["hr_bpm", "n_synth"] == 140 and out.loc["hr_bpm", "n_real"] == 200
    assert out.loc["hr_bpm", "ks_D"] < 0.2 < 0.8 < out.loc["qrs_duration_ms", "ks_D"]
    assert out.loc["qrs_duration_ms", "ks_p_adjusted"] < 1e-6
    assert out.loc["qrs_duration_ms", "cohens_d"] == pytest.approx(3.5, abs=0.5)
    assert (out["ks_p_adjusted"] >= out["ks_p"] - 1e-15).all()
    empty = compare_feature_distributions(real_df, synth_df.assign(hr_bpm=np.nan), ["hr_bpm"])
    assert np.isnan(empty.loc[0, "ks_D"]) and empty.loc[0, "n_synth"] == 0


# ------------------------------------------------------------------ #
# Report and CLI                                                       #
# ------------------------------------------------------------------ #

def test_gallery_indices(real, synth):
    assert gallery_indices(real, [synth], 3) == [0, 1, 2]
    rnd = gallery_indices(real, [synth], 3, "random", seed=1)
    assert rnd == gallery_indices(real, [synth], 3, "random", seed=1)
    assert len(set(rnd)) == 3 and max(rnd) < synth.n_samples
    with pytest.raises(ValueError):
        gallery_indices(real, [synth], 3, "best")


def test_report_sections(real, synth, tmp_path):
    results = {
        key: {synth.label: AVAILABLE_METRICS[key]().compute(real.data, synth.data, real.lead_names)}
        for key in ("pearson", "js_div", "c2st", "ks_test")
    }
    emb = plot_embedding_2d(compute_embedding_2d(real, [synth]))
    rng = np.random.default_rng(2)
    feats = [pd.DataFrame({"hr_bpm": rng.normal(70, 8, n)}) for n in (24, 20)]
    out = generate_report(real, [synth], results, tmp_path / "r.html", n_ecg_samples=2,
                          embedding_plots=[emb], gallery_selection="random",
                          feature_df_real=feats[0], feature_dfs_synth=[feats[1]])
    html = out.read_text(encoding="utf-8")
    for needle in ("<h2>Beat Morphology</h2>", "<h2>Embedding Projections</h2>",
                   "Real vs real (baseline)", "Pairing: <code>nn</code>", "Classifier accuracy",
                   "Share of tests rejected", "Amplitude Distribution per Lead",
                   "random (seed 42)", "Model A KS D"):
        assert needle in html, needle
    plain = generate_report(real, [synth], {}, tmp_path / "p.html", n_ecg_samples=1,
                            beat_bands=False).read_text(encoding="utf-8")
    assert "Beat Morphology" not in plain and "Embedding Projections" not in plain


@pytest.fixture
def npy_files(real, synth, tmp_path):
    np.save(tmp_path / "real.npy", real.data)
    np.save(tmp_path / "synth.npy", synth.data[:, :, :])
    np.save(tmp_path / "paired.npy", real.data * 1.1)
    return str(tmp_path / "real.npy"), str(tmp_path / "synth.npy"), str(tmp_path / "paired.npy")


def test_cli_pairing_is_forwarded(npy_files, tmp_path, monkeypatch):
    seen = {}

    class Recording(AVAILABLE_METRICS["pearson"]):
        def __init__(self, pairing="nn", fs=500.0, **kwargs):
            seen.update(pairing=pairing, fs=fs)
            super().__init__(pairing=pairing, fs=fs, **kwargs)

    monkeypatch.setitem(AVAILABLE_METRICS, "pearson", Recording)
    real, synth, paired = npy_files
    args = ["eval", "-r", real, "--fs", "250", "-m", "pearson", "-m", "mmd",
            "-o", str(tmp_path / "r.html"), "--no-beat-bands"]
    ok = CliRunner().invoke(cli.main, args + ["-s", paired, "--pairing", "paired"])
    assert ok.exit_code == 0, ok.output
    assert seen == {"pairing": "paired", "fs": 250.0}
    bad = CliRunner().invoke(cli.main, args + ["-s", synth, "--pairing", "paired"])
    assert bad.exit_code != 0 and "same number of recordings" in bad.output


def test_cli_embedding_and_beat_options(npy_files, tmp_path):
    real, synth, _ = npy_files
    out = tmp_path / "r.html"
    res = CliRunner().invoke(cli.main, [
        "eval", "-r", real, "-s", synth, "--fs", "250", "-m", "mse", "-o", str(out),
        "--embedding-plots", "--embedding-method", "pca", "--gallery-selection", "random"])
    assert res.exit_code == 0, res.output
    html = out.read_text(encoding="utf-8")
    assert "Embedding Projections" in html and "Beat Morphology" in html

    for mode in ("beats", "beat-density"):
        v = tmp_path / f"{mode}.html"
        res = CliRunner().invoke(cli.main, ["visualize", "-r", real, "-s", synth, "--fs", "250",
                                            "--compare-mode", mode, "-o", str(v)])
        assert res.exit_code == 0, res.output
        assert v.stat().st_size > 10_000
    v = tmp_path / "peaks.html"
    res = CliRunner().invoke(cli.main, ["visualize", "-r", real, "-s", synth, "--fs", "250",
                                        "--n-samples", "1", "--show-r-peaks", "--embedding", "pca",
                                        "-o", str(v)])
    assert res.exit_code == 0, res.output
    assert "triangle-down-open" in v.read_text(encoding="utf-8")


def test_cli_features_stats_output(npy_files, tmp_path):
    pytest.importorskip("scipy")
    real, synth, _ = npy_files
    stats = tmp_path / "stats.csv"
    res = CliRunner().invoke(cli.main, [
        "features", "-r", real, "-s", synth, "--fs", "250", "--lead", "L2",
        "--feature-backend", "scipy", "-o", str(tmp_path / "f.csv"), "--stats-output", str(stats)])
    assert res.exit_code == 0, res.output
    df = pd.read_csv(stats)
    assert {"dataset", "feature", "ks_D", "ks_p_adjusted", "mwu_p", "cohens_d"} <= set(df.columns)
    assert "hr_bpm" in set(df["feature"])
