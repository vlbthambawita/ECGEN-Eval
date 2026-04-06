"""
Tests for the Fréchet ECG Distance (FED) metric.

These tests are designed to run without a network connection and without
requiring model weights to be downloaded.  The integration test that
actually runs encode() uses a mock encoder injected directly onto the
FEDMetric instance.

A separate optional test (marked with ``pytest.mark.slow``) tests the full
end-to-end path with real HuggingFace downloads — skip it by default with
``pytest -m "not slow"``.
"""

from __future__ import annotations

import importlib
import sys
import types

import numpy as np
import pytest

from ecgen_eval.metrics import AVAILABLE_METRICS
from ecgen_eval.metrics.fed import FEDMetric
from ecgen_eval.metrics.base import MetricResult


# ------------------------------------------------------------------ #
# Helpers                                                              #
# ------------------------------------------------------------------ #

def _make(n: int, leads: int = 12, t: int = 500, seed: int = 0) -> np.ndarray:
    return np.random.default_rng(seed).standard_normal((n, leads, t)).astype(np.float32)


class _MockEncoder:
    """Deterministic mock encoder: returns random (N, 16) embeddings."""

    def __init__(self, embed_dim: int = 16, seed: int = 99):
        self._rng = np.random.default_rng(seed)
        self.embed_dim = embed_dim

    def encode(self, signals: np.ndarray) -> np.ndarray:
        N = signals.shape[0]
        return self._rng.standard_normal((N, self.embed_dim)).astype(np.float64)


# ------------------------------------------------------------------ #
# Test 1 — 'fed' key is registered in AVAILABLE_METRICS               #
# ------------------------------------------------------------------ #

def test_fed_registered():
    assert "fed" in AVAILABLE_METRICS, "'fed' must be registered in AVAILABLE_METRICS"
    assert AVAILABLE_METRICS["fed"] is FEDMetric


# ------------------------------------------------------------------ #
# Test 2 — FEDMetric can be constructed without torch                  #
# ------------------------------------------------------------------ #

def test_fed_instantiation_without_torch(monkeypatch):
    """FEDMetric can be constructed even when torch is not installed."""
    # Hide torch from the import system temporarily
    monkeypatch.setitem(sys.modules, "torch", None)

    metric = FEDMetric(backbone="ecgfounder")
    assert metric.backbone == "ecgfounder"
    assert metric._encoder is None  # lazy — not loaded yet


# ------------------------------------------------------------------ #
# Test 3 — compute() raises ImportError when torch is missing         #
# ------------------------------------------------------------------ #

def test_fed_compute_raises_without_torch(monkeypatch):
    """compute() must raise ImportError with a helpful message when torch is absent."""
    # Make the encoder factory raise ImportError (simulates missing torch)
    def _fake_get_encoder(name, device, batch_size):
        raise ImportError("torch is required … pip install ecgen-eval[fed]")

    metric = FEDMetric(backbone="ecgfounder")

    monkeypatch.setattr(
        "ecgen_eval.metrics.fed.FEDMetric._encoder",
        None,
        raising=False,
    )

    # Patch the factory used inside compute()
    import ecgen_eval.metrics.encoders as enc_pkg
    monkeypatch.setattr(enc_pkg, "get_encoder", _fake_get_encoder)

    real = _make(10)
    synth = _make(10, seed=1)

    with pytest.raises(ImportError, match="pip install ecgen-eval"):
        metric.compute(real, synth)


# ------------------------------------------------------------------ #
# Test 4 — compute() returns a valid MetricResult with mock encoder   #
# ------------------------------------------------------------------ #

def test_fed_compute_mock_encoder():
    """compute() returns a finite, non-negative MetricResult when using a mock encoder."""
    real = _make(20, leads=12, t=500, seed=0)
    synth = _make(20, leads=12, t=500, seed=1)

    metric = FEDMetric(backbone="ecgfounder")
    # Inject mock encoder so no download is attempted
    metric._encoder = _MockEncoder(embed_dim=16)

    result = metric.compute(real, synth)

    assert isinstance(result, MetricResult)
    assert result.metric_name == "fed"
    assert np.isfinite(result.score)
    assert result.score >= 0.0
    assert result.higher_is_better is False
    assert result.per_lead_scores == {}
    assert result.extra.get("backbone") == "ecgfounder"


# ------------------------------------------------------------------ #
# Test 5 — identical distributions produce a near-zero score          #
# ------------------------------------------------------------------ #

def test_fed_identical_distributions_near_zero():
    """FED of a set against itself should be very close to 0."""
    real = _make(50, leads=12, t=500, seed=42)

    metric = FEDMetric()
    metric._encoder = _MockEncoder(embed_dim=32, seed=7)

    # Encode real once, then pretend both real and synth are the same array
    emb = metric._encoder.encode(real)

    # Directly call frechet_distance
    from ecgen_eval.metrics._frechet_utils import frechet_distance
    score = frechet_distance(emb, emb)
    assert score < 1e-6, f"Expected ~0 for identical inputs, got {score}"


# ------------------------------------------------------------------ #
# Test 6 — different backbones can be instantiated                    #
# ------------------------------------------------------------------ #

@pytest.mark.parametrize("backbone", ["ecgfounder", "hubert_ecg", "ecgfm"])
def test_fed_backbone_variants(backbone):
    """All supported backbone names should be accepted without error."""
    metric = FEDMetric(backbone=backbone, device="cpu", batch_size=8)
    assert metric.backbone == backbone
    assert metric._encoder is None  # still lazy


# ------------------------------------------------------------------ #
# Test 7 — unknown backbone raises ValueError at encode time          #
# ------------------------------------------------------------------ #

def test_fed_unknown_backbone():
    metric = FEDMetric(backbone="nonexistent_model")
    real = _make(5)
    synth = _make(5, seed=1)

    with pytest.raises(ValueError, match="Unknown backbone"):
        metric.compute(real, synth)


# ------------------------------------------------------------------ #
# Test 8 — subsampling works correctly                                 #
# ------------------------------------------------------------------ #

def test_fed_subsampling():
    """n_subsample caps the number of recordings passed to the encoder."""
    real = _make(100, leads=12, t=200, seed=0)
    synth = _make(100, leads=12, t=200, seed=1)

    encoded_shapes = []

    class _TrackingEncoder:
        def encode(self, signals):
            encoded_shapes.append(signals.shape[0])
            rng = np.random.default_rng(0)
            return rng.standard_normal((signals.shape[0], 8))

    metric = FEDMetric(n_subsample=20)
    metric._encoder = _TrackingEncoder()

    metric.compute(real, synth)

    assert all(n <= 20 for n in encoded_shapes), (
        f"Encoder received more than n_subsample recordings: {encoded_shapes}"
    )
