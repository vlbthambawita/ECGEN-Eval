"""
Amplitude-distribution Jensen–Shannon / Kullback–Leibler divergence for ECG evaluation.

Reference
---------
Lin, J. (1991).
Divergence measures based on the Shannon entropy.
*IEEE Transactions on Information Theory*, 37(1), 145–151.
https://doi.org/10.1109/18.61115

Kullback, S., & Leibler, R. A. (1951).
On information and sufficiency.
*The Annals of Mathematical Statistics*, 22(1), 79–86.
https://doi.org/10.1214/aoms/1177729694

Implementation notes
--------------------
Per lead:

1. Pool the amplitude values of all (subsampled) real recordings, and of all
   synthetic recordings.
2. Build bins from the **real** data: ``n_bins`` equal bins between the 0.1st and
   99.9th real percentile, plus one open-ended bin on each side. Synthetic values
   outside the real range are therefore counted (in the tail bins), not dropped.
3. Normalise both histograms to probabilities P (real) and Q (synthetic) and compute

     JS(P ‖ Q) = ½ KL(P ‖ M) + ½ KL(Q ‖ M),   M = ½ (P + Q)

The score is JS because it is symmetric, bounded by ln 2 and finite for empty bins.
KL in both directions (with ``eps`` smoothing) is reported in ``extra`` because many
papers quote KL.

The temporal order of the samples plays no role: this metric sees gain, offset,
clipping and noise-floor differences, not morphology.
"""

from __future__ import annotations

from typing import List, Optional

import numpy as np

from ecgen_eval.metrics._divergence import js_divergence, kl_divergence
from ecgen_eval.metrics._matching import subsample
from ecgen_eval.metrics.base import BaseMetric, MetricResult

_REFERENCE = (
    "Lin, J. (1991). Divergence measures based on the Shannon entropy. IEEE Transactions on "
    "Information Theory, 37(1), 145–151. https://doi.org/10.1109/18.61115"
)

_DESCRIPTION = (
    "Amplitude JS Divergence: Jensen–Shannon divergence between the amplitude-value "
    "distributions of real and synthetic ECGs, per lead (KL in extra). Lower is better."
)


class AmplitudeJSMetric(BaseMetric):
    """
    Jensen–Shannon divergence between pooled amplitude histograms, per lead.

    Parameters
    ----------
    n_bins : int
        Number of equal bins between the 0.1st and 99.9th real percentile (two
        open-ended tail bins are added). Default: 100.
    n_subsample : int
        Max recordings per set. Default: 1000.
    eps : float
        Smoothing added to every bin for the KL values in ``extra``. Default: 1e-10.
    seed : int
        Random seed. Default: 42.
    """

    name = "js_div"
    description = _DESCRIPTION
    reference = _REFERENCE
    higher_is_better = False

    def __init__(
        self, n_bins: int = 100, n_subsample: int = 1000, eps: float = 1e-10, seed: int = 42
    ):
        self.n_bins = n_bins
        self.n_subsample = n_subsample
        self.eps = eps
        self.seed = seed

    def compute(
        self,
        real: np.ndarray,
        synth: np.ndarray,
        lead_names: Optional[List[str]] = None,
    ) -> MetricResult:
        self._check_inputs(real, synth)
        n_leads = real.shape[1]
        if lead_names is None:
            lead_names = [f"L{i+1}" for i in range(n_leads)]

        rng = np.random.default_rng(self.seed)
        per_lead: dict = {}
        kl_rs: dict = {}
        kl_sr: dict = {}
        js_dist: dict = {}
        tail: dict = {}
        hist_r: dict = {}
        hist_s: dict = {}
        edges_out: dict = {}

        for li, lname in enumerate(lead_names):
            r = subsample(real[:, li, :], self.n_subsample, rng).astype(np.float64).ravel()
            s = subsample(synth[:, li, :], self.n_subsample, rng).astype(np.float64).ravel()
            edges = self._edges(r, s)
            p = self._histogram(r, edges)
            q = self._histogram(s, edges)

            js = float(np.clip(js_divergence(p, q), 0.0, np.log(2)))
            per_lead[lname] = js
            js_dist[lname] = float(np.sqrt(js))
            kl_rs[lname] = kl_divergence(p, q, self.eps)
            kl_sr[lname] = kl_divergence(q, p, self.eps)
            tail[lname] = float(q[0] + q[-1])
            hist_r[lname] = p.tolist()
            hist_s[lname] = q.tolist()
            edges_out[lname] = edges.tolist()

        return MetricResult(
            metric_name=self.name,
            score=float(np.mean(list(per_lead.values()))),
            higher_is_better=self.higher_is_better,
            per_lead_scores=per_lead,
            description=self.description,
            reference=self.reference,
            extra={
                "per_lead_kl_real_synth": kl_rs,
                "per_lead_kl_synth_real": kl_sr,
                "kl_real_synth": float(np.mean(list(kl_rs.values()))),
                "kl_synth_real": float(np.mean(list(kl_sr.values()))),
                "per_lead_js_distance": js_dist,
                "per_lead_tail_mass": tail,
                "per_lead_hist_real": hist_r,
                "per_lead_hist_synth": hist_s,
                "bin_edges": edges_out,
                "n_bins": self.n_bins,
            },
        )

    def _edges(self, r: np.ndarray, s: np.ndarray) -> np.ndarray:
        """Finite bin edges (``n_bins + 1`` values) taken from the real data."""
        lo, hi = np.percentile(r, [0.1, 99.9])
        if hi <= lo:  # constant real lead: fall back to the pooled range
            lo = min(r.min(), s.min())
            hi = max(r.max(), s.max())
        if hi <= lo:
            lo, hi = lo - 0.5, lo + 0.5
        return np.linspace(lo, hi, self.n_bins + 1)

    @staticmethod
    def _histogram(x: np.ndarray, edges: np.ndarray) -> np.ndarray:
        """Probabilities over ``[−inf, e0), [e0, e1), ..., [e_n, +inf)``."""
        idx = np.searchsorted(edges, x, side="right")
        idx[x == edges[-1]] = len(edges) - 1  # right edge belongs to the last finite bin
        counts = np.bincount(idx, minlength=len(edges) + 1).astype(np.float64)
        return counts / max(counts.sum(), 1.0)
