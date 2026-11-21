"""Tests for the ecgen-eval CLI."""

import numpy as np
import pytest
from click.testing import CliRunner

from ecgen_eval import cli
from ecgen_eval.metrics import AVAILABLE_METRICS


def _save(path, seed, n=8, leads=12, t=1000):
    arr = np.random.default_rng(seed).standard_normal((n, leads, t)).astype(np.float32)
    np.save(path, arr)
    return str(path)


@pytest.fixture
def npy_pair(tmp_path):
    return _save(tmp_path / "real.npy", 0), _save(tmp_path / "synth.npy", 1)


def test_default_metrics_are_a_curated_subset():
    assert cli.DEFAULT_METRICS == [
        "fd", "mmd", "pr_dist", "c2st", "rmse", "pearson", "dtw", "js_div", "psd",
        "heart_rate", "hrv", "nn_dist",
    ]
    assert set(cli.DEFAULT_METRICS) < set(AVAILABLE_METRICS)
    assert "fed" not in cli.DEFAULT_METRICS


def test_all_metrics_exclude_fed():
    assert set(cli.ALL_METRICS) == set(AVAILABLE_METRICS) - {"fed"}


def test_resolve_metrics():
    assert cli.resolve_metrics(["MMD", "prd", "mmd"]) == ["mmd", "prd"]
    assert cli.resolve_metrics(["all"]) == cli.ALL_METRICS
    with_fed = cli.resolve_metrics(["all", "fed"])
    assert with_fed[-1] == "fed" and len(with_fed) == len(AVAILABLE_METRICS)
    assert cli.resolve_metrics(["rmse", "all"])[0] == "rmse"


def test_eval_default_and_all(npy_pair, tmp_path, monkeypatch):
    ran = []

    def fake_report(metric_results, output_path, **kwargs):
        ran.append(list(metric_results))
        return tmp_path / "unused.html"

    monkeypatch.setattr(cli, "generate_report", fake_report)
    real, synth = npy_pair
    base = ["eval", "-r", real, "-s", synth, "-o", str(tmp_path / "r.html")]
    assert CliRunner().invoke(cli.main, base).exit_code == 0
    assert CliRunner().invoke(cli.main, base + ["-m", "all"]).exit_code == 0
    assert ran == [cli.DEFAULT_METRICS, cli.ALL_METRICS]
    bad = CliRunner().invoke(cli.main, base + ["-m", "everything"])
    assert bad.exit_code != 0


def test_eval_forwards_fs_to_metrics(npy_pair, tmp_path, monkeypatch):
    seen = {}

    class RecordingPSD(AVAILABLE_METRICS["psd"]):
        def __init__(self, fs=500.0, **kwargs):
            seen["fs"] = fs
            super().__init__(fs=fs, **kwargs)

    monkeypatch.setitem(AVAILABLE_METRICS, "psd", RecordingPSD)
    real, synth = npy_pair
    result = CliRunner().invoke(
        cli.main,
        ["eval", "-r", real, "-s", synth, "-m", "psd", "-m", "mmd",
         "--fs", "250", "-o", str(tmp_path / "report.html")],
    )
    assert result.exit_code == 0, result.output
    assert seen["fs"] == 250.0
    assert (tmp_path / "report.html").exists()


def test_list_features_shows_backends():
    result = CliRunner().invoke(cli.main, ["list-features"])
    assert result.exit_code == 0, result.output
    for name in ("hybrid", "neurokit2", "scipy", "biosppy", "heartpy"):
        assert name in result.output
    assert "--rpeak-method: hamilton" in result.output


@pytest.mark.parametrize("backend, option", [
    ("scipy", ["--delineation-method", "dwt"]),
    ("heartpy", ["--rpeak-method", "neurokit"]),
    ("biosppy", ["--rpeak-method", "neurokit"]),
])
def test_features_rejects_backend_options(npy_pair, tmp_path, backend, option):
    real, _ = npy_pair
    result = CliRunner().invoke(
        cli.main,
        ["features", "-r", real, "--feature-backend", backend, *option,
         "-o", str(tmp_path / "f.csv")],
    )
    assert result.exit_code == 2
    assert option[0] in result.output


@pytest.mark.parametrize("backend", ["biosppy", "heartpy"])
def test_features_with_new_backends(tmp_path, backend):
    pytest.importorskip(backend)
    from tests.test_features import _synthetic_ecg

    np.save(tmp_path / "real.npy", np.stack([_synthetic_ecg(seed=s) for s in range(2)])
            .astype(np.float32))
    out = tmp_path / "f.csv"
    result = CliRunner().invoke(
        cli.main,
        ["features", "-r", str(tmp_path / "real.npy"), "--feature-backend", backend,
         "-F", "rhythm", "-F", "hrv", "-o", str(out)],
    )
    assert result.exit_code == 0, result.output
    import pandas as pd

    df = pd.read_csv(out)
    assert df["hr_bpm"].between(70, 80).all()
