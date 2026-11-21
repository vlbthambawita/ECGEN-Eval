"""Base class for metrics that score matched (real, synthetic) signal pairs per lead."""

from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np

from ecgen_eval.metrics._matching import check_pairing, matched_pairs, split_half
from ecgen_eval.metrics.base import BaseMetric, MetricResult

NORMALIZATIONS = (None, "zscore", "minmax")


def normalize_rows(X: np.ndarray, mode: Optional[str]) -> np.ndarray:
    """Normalise each row (one recording, one lead) of ``X``."""
    X = np.asarray(X, dtype=np.float64)
    if mode is None:
        return X
    if mode == "zscore":
        return (X - X.mean(axis=1, keepdims=True)) / (X.std(axis=1, keepdims=True) + 1e-12)
    if mode == "minmax":
        lo = X.min(axis=1, keepdims=True)
        return (X - lo) / (X.max(axis=1, keepdims=True) - lo + 1e-12)
    raise ValueError(f"Unknown normalize {mode!r}. Choose one of {NORMALIZATIONS}.")


class PairwiseSignalMetric(BaseMetric):
    """
    Per lead: build matched (real, synthetic) pairs, score every pair with
    :meth:`_pair_values`, and average.

    Subclasses implement :meth:`_pair_values` and may override :meth:`_match_key`
    (representation used for the nearest-neighbour search), :meth:`_prepare`
    (per-lead preprocessing) and :meth:`_lead_extra` (extra per-lead numbers).

    ``extra`` always contains ``pairing``, ``per_lead_std``, ``per_lead_median``,
    ``per_lead_all_values`` (one value per pair), ``per_lead_n_pairs``, ``n_skipped``
    and, when ``baseline`` is on, ``real_vs_real`` / ``per_lead_real_vs_real``: the
    same statistic between two disjoint halves of the real set.
    """

    #: Max synthetic rows searched in 'nn' mode; ``None`` means ``n_subsample``.
    n_candidates: Optional[int] = None
    #: Whether ``normalize`` is a user-facing option of the metric (reported in ``extra``).
    _report_normalize: bool = False

    def __init__(
        self,
        pairing: str = "nn",
        n_subsample: int = 500,
        normalize: Optional[str] = None,
        baseline: bool = True,
        seed: int = 42,
    ):
        self.pairing = check_pairing(pairing)
        if normalize not in NORMALIZATIONS:
            raise ValueError(f"Unknown normalize {normalize!r}. Choose one of {NORMALIZATIONS}.")
        self.n_subsample = n_subsample
        self.normalize = normalize
        self.baseline = baseline
        self.seed = seed

    # ------------------------------------------------------------------ #
    # Hooks                                                                #
    # ------------------------------------------------------------------ #

    def _pair_values(self, R: np.ndarray, S: np.ndarray) -> np.ndarray:
        """Score row-aligned pairs. ``(M, T), (M, T) -> (M,)``; NaN marks a skipped pair."""
        raise NotImplementedError

    def _match_key(self, X: np.ndarray) -> np.ndarray:
        """Representation used to find nearest neighbours (default: the signal itself)."""
        return X

    def _prepare(self, X: np.ndarray) -> np.ndarray:
        """Per-lead preprocessing applied before matching."""
        return normalize_rows(X, self.normalize)

    def _lead_extra(self, R: np.ndarray, S: np.ndarray, values: np.ndarray) -> Dict[str, float]:
        """Additional per-lead numbers; each key ``k`` is stored as ``per_lead_k`` and ``k``."""
        return {}

    # ------------------------------------------------------------------ #
    # BaseMetric interface                                                 #
    # ------------------------------------------------------------------ #

    def compute(
        self,
        real: np.ndarray,
        synth: np.ndarray,
        lead_names: Optional[List[str]] = None,
    ) -> MetricResult:
        self._check_inputs(real, synth)
        if real.shape[2] != synth.shape[2]:
            raise ValueError(
                f"Signal length mismatch: real has {real.shape[2]} samples, "
                f"synth has {synth.shape[2]}"
            )
        n_leads = real.shape[1]
        if lead_names is None:
            lead_names = [f"L{i+1}" for i in range(n_leads)]

        rng = np.random.default_rng(self.seed)
        rng_base = np.random.default_rng(self.seed + 1)  # keeps scores independent of `baseline`

        per_lead: Dict[str, float] = {}
        per_std: Dict[str, float] = {}
        per_median: Dict[str, float] = {}
        per_values: Dict[str, List[float]] = {}
        per_n: Dict[str, int] = {}
        per_base: Dict[str, float] = {}
        lead_extras: Dict[str, Dict[str, float]] = {}
        n_skipped = 0

        for li, lname in enumerate(lead_names):
            R = self._prepare(real[:, li, :])
            S = self._prepare(synth[:, li, :])
            Rm, Sm = matched_pairs(
                R, S, self.pairing, self.n_subsample, rng,
                key=self._match_key, n_candidates=self.n_candidates,
            )
            values = np.asarray(self._pair_values(Rm, Sm), dtype=np.float64)
            ok = np.isfinite(values)
            n_skipped += int((~ok).sum())
            good = values[ok]
            per_lead[lname] = float(good.mean()) if good.size else float("nan")
            per_std[lname] = float(good.std()) if good.size else float("nan")
            per_median[lname] = float(np.median(good)) if good.size else float("nan")
            per_values[lname] = [float(v) for v in good]
            per_n[lname] = int(good.size)
            for k, v in self._lead_extra(Rm, Sm, values).items():
                lead_extras.setdefault(k, {})[lname] = float(v)

            if self.baseline:
                per_base[lname] = self._baseline(R, rng_base)

        extra = {
            "pairing": self.pairing,
            "per_lead_std": per_std,
            "per_lead_median": per_median,
            "per_lead_all_values": per_values,
            "per_lead_n_pairs": per_n,
            "n_skipped": n_skipped,
        }
        if self._report_normalize:
            extra["normalize"] = self.normalize
        for k, by_lead in lead_extras.items():
            extra[f"per_lead_{k}"] = by_lead
            extra[k] = _nanmean(by_lead.values())
        if self.baseline:
            extra["per_lead_real_vs_real"] = per_base
            extra["real_vs_real"] = _nanmean(per_base.values())

        return MetricResult(
            metric_name=self.name,
            score=_nanmean(per_lead.values()),
            higher_is_better=self.higher_is_better,
            per_lead_scores=per_lead,
            description=self.description,
            reference=self.reference,
            extra=extra,
        )

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _baseline(self, R: np.ndarray, rng: np.random.Generator) -> float:
        """Same statistic between two disjoint halves of the (prepared) real lead."""
        if R.shape[0] < 2:
            return float("nan")
        A, B = split_half(R, rng)
        Am, Bm = matched_pairs(
            A, B, self.pairing, self.n_subsample, rng,
            key=self._match_key, n_candidates=self.n_candidates,
        )
        values = np.asarray(self._pair_values(Am, Bm), dtype=np.float64)
        values = values[np.isfinite(values)]
        return float(values.mean()) if values.size else float("nan")

def _nanmean(values) -> float:
    arr = np.asarray(list(values), dtype=np.float64)
    arr = arr[np.isfinite(arr)]
    return float(arr.mean()) if arr.size else float("nan")
