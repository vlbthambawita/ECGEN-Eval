"""Tests for the shared pairing helper (ecgen_eval.metrics._matching)."""

import numpy as np
import pytest

from ecgen_eval.metrics._matching import (
    PAIRINGS,
    check_pairing,
    matched_pairs,
    nearest_neighbour,
    split_half,
    subsample,
    subsample_paired,
)


def _rand(n, t=40, seed=0):
    return np.random.default_rng(seed).standard_normal((n, t))


def test_pairings_and_validation():
    assert PAIRINGS == ("nn", "paired", "mean")
    assert check_pairing("NN") == "nn"
    with pytest.raises(ValueError):
        check_pairing("closest")


def test_nearest_neighbour_matches_brute_force():
    R, S = _rand(37, seed=1), _rand(53, seed=2)
    brute = np.array([np.argmin(((S - r) ** 2).sum(axis=1)) for r in R])
    assert np.array_equal(nearest_neighbour(R, S, chunk=8), brute)


def test_nn_pairs_are_row_aligned_nearest_neighbours():
    R, S = _rand(20, seed=3), _rand(30, seed=4)
    Rm, Sm = matched_pairs(R, S, "nn", n_subsample=100, rng=np.random.default_rng(0))
    assert Rm.shape == Sm.shape == R.shape
    assert np.array_equal(Sm, S[nearest_neighbour(R, S)])


def test_nn_key_changes_the_neighbour_search_only():
    R = np.array([[1.0, 2.0, 3.0]])
    S = np.array([[1.1, 2.1, 3.1], [10.0, 20.0, 30.0]])  # row 1 is R scaled by 10
    unit = lambda X: X / np.linalg.norm(X, axis=1, keepdims=True)  # noqa: E731
    _, raw = matched_pairs(R, S, "nn", rng=np.random.default_rng(0))
    _, by_dir = matched_pairs(R, S, "nn", rng=np.random.default_rng(0), key=unit)
    assert np.array_equal(raw[0], S[0])
    assert np.array_equal(by_dir[0], S[1])  # returns the original rows, not the key


def test_paired_requires_equal_counts():
    with pytest.raises(ValueError, match="same number"):
        matched_pairs(_rand(5), _rand(6), "paired", rng=np.random.default_rng(0))


def test_paired_subsampling_keeps_rows_aligned():
    R = _rand(50, seed=5)
    S = R + 1.0
    Rm, Sm = subsample_paired(R, S, 10, np.random.default_rng(0))
    assert Rm.shape == (10, 40)
    assert np.allclose(Sm - Rm, 1.0)


def test_mean_pairing_returns_one_pair():
    R, S = _rand(12, seed=6), _rand(9, seed=7)
    Rm, Sm = matched_pairs(R, S, "mean", rng=np.random.default_rng(0))
    assert Rm.shape == Sm.shape == (1, 40)
    assert np.allclose(Rm[0], R.mean(axis=0)) and np.allclose(Sm[0], S.mean(axis=0))


def test_split_half_is_disjoint_and_equal_sized():
    R = np.arange(11, dtype=float)[:, None] * np.ones((1, 3))
    A, B = split_half(R, np.random.default_rng(0))
    assert A.shape == B.shape == (5, 3)
    assert not set(A[:, 0]) & set(B[:, 0])


def test_subsample_and_determinism():
    R = _rand(100, seed=8)
    assert subsample(R, 200, np.random.default_rng(0)) is R
    a = subsample(R, 10, np.random.default_rng(3))
    b = subsample(R, 10, np.random.default_rng(3))
    assert a.shape == (10, 40) and np.array_equal(a, b)


def test_empty_set_raises():
    with pytest.raises(ValueError):
        matched_pairs(_rand(0), _rand(3), "nn", rng=np.random.default_rng(0))
