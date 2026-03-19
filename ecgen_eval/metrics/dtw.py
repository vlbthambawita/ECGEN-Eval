"""
Dynamic Time Warping (DTW) distance metric for ECG evaluation.

References
----------
Primary algorithm:
  Berndt, D. J., & Clifford, J. (1994).
  Using dynamic time warping to find patterns in time series.
  *KDD Workshop*, 10(16), 359–370.

ECG-specific application:
  Clifford, G. D., Liu, C., Moody, B., et al. (2017).
  AF classification from a short single lead ECG recording:
  The PhysioNet/Computing in Cardiology Challenge 2017.
  *Computing in Cardiology*, 44. https://doi.org/10.22489/CinC.2017.065-469

  Goldberger, A. L., et al. (2000).
  PhysioBank, PhysioToolkit, and PhysioNet: Components of a new research
  resource for complex physiologic signals.
  *Circulation*, 101(23), e215–e220. https://doi.org/10.1161/01.CIR.101.23.e215

Implementation notes
--------------------
Computing DTW between every real–synthetic pair is O(N_r × N_s × T²) and
prohibitively expensive for large datasets. We therefore:

1. Randomly sample `n_pairs` (real, synthetic) pairs.
2. Compute DTW on downsampled signals (stride `downsample`) to reduce T.
3. Report the mean DTW distance across sampled pairs, both globally and per lead.

The dtaidistance library (pip install dtaidistance) provides a fast Cython
implementation of DTW with optional Sakoe-Chiba band constraint.
"""

from __future__ import annotations

from typing import List, Optional

import numpy as np

from ecgen_eval.metrics.base import BaseMetric, MetricResult


_REFERENCE = (
    "Berndt, D. J., & Clifford, J. (1994). Using dynamic time warping to find patterns in "
    "time series. KDD Workshop, 10(16), 359–370. | "
    "Goldberger, A. L., et al. (2000). PhysioBank, PhysioToolkit, and PhysioNet. "
    "Circulation, 101(23), e215–e220. https://doi.org/10.1161/01.CIR.101.23.e215"
)

_DESCRIPTION = (
    "Dynamic Time Warping (DTW): measures morphological shape similarity between real and "
    "synthetic ECG waveforms by finding the optimal non-linear alignment along the time axis. "
    "Mean pairwise DTW distance over randomly sampled pairs. Lower is better."
)


class DTWMetric(BaseMetric):
    """
    Mean pairwise DTW distance between random (real, synthetic) pairs per lead.

    Parameters
    ----------
    n_pairs : int
        Number of (real, synthetic) pairs to sample. Default: 200.
    downsample : int
        Take every `downsample`-th sample before computing DTW (speed trade-off).
        Default: 5 (500 Hz → 100 Hz effective, 5000 pts → 1000 pts).
    window : float
        Sakoe-Chiba band as a fraction of signal length (0–1). Default: 0.1.
    seed : int
        Random seed for reproducibility.
    """

    name = "dtw"
    description = _DESCRIPTION
    reference = _REFERENCE
    higher_is_better = False

    def __init__(
        self,
        n_pairs: int = 200,
        downsample: int = 5,
        window: float = 0.1,
        seed: int = 42,
    ):
        self.n_pairs = n_pairs
        self.downsample = downsample
        self.window = window
        self.seed = seed

    # ------------------------------------------------------------------ #
    # Public                                                               #
    # ------------------------------------------------------------------ #

    def compute(
        self,
        real: np.ndarray,
        synth: np.ndarray,
        lead_names: Optional[List[str]] = None,
    ) -> MetricResult:
        """
        Parameters
        ----------
        real  : (N_r, L, T)
        synth : (N_s, L, T)
        """
        self._check_inputs(real, synth)
        n_leads = real.shape[1]
        if lead_names is None:
            lead_names = [f"L{i+1}" for i in range(n_leads)]

        rng = np.random.default_rng(self.seed)
        r_idx = rng.integers(0, real.shape[0], size=self.n_pairs)
        s_idx = rng.integers(0, synth.shape[0], size=self.n_pairs)

        dtw_fn = self._get_dtw_fn()

        per_lead: dict = {}
        per_lead_all_dists: dict = {}

        for li, lname in enumerate(lead_names):
            dists = []
            for ri, si in zip(r_idx, s_idx):
                r_sig = real[ri, li, :: self.downsample].astype(np.float64)
                s_sig = synth[si, li, :: self.downsample].astype(np.float64)
                d = dtw_fn(r_sig, s_sig)
                dists.append(d)
            per_lead[lname] = float(np.mean(dists))
            per_lead_all_dists[lname] = [float(x) for x in dists]

        overall = float(np.mean(list(per_lead.values())))

        return MetricResult(
            metric_name=self.name,
            score=overall,
            higher_is_better=self.higher_is_better,
            per_lead_scores=per_lead,
            description=self.description,
            reference=self.reference,
            extra={
                "per_lead_dtw": per_lead,
                "per_lead_all_distances": per_lead_all_dists,
                "n_pairs": self.n_pairs,
                "downsample_factor": self.downsample,
                "window_fraction": self.window,
            },
        )

    # ------------------------------------------------------------------ #
    # DTW backend selection                                                #
    # ------------------------------------------------------------------ #

    def _get_dtw_fn(self):
        """
        Try dtaidistance (fast Cython) first; fall back to pure-Python
        implementation if not installed.
        """
        try:
            from dtaidistance import dtw as _dtw_lib

            window_abs = None  # will be set per-call in closure

            def dtw_fast(a, b):
                w = max(1, int(self.window * len(a)))
                return _dtw_lib.distance_fast(a, b, window=w, use_pruning=True)

            return dtw_fast
        except ImportError:
            return self._dtw_pure

    def _dtw_pure(self, a: np.ndarray, b: np.ndarray) -> float:
        """
        Pure-NumPy DTW with Sakoe-Chiba band.
        O(n * w) time and space where w = window samples.
        """
        n, m = len(a), len(b)
        w = max(1, int(self.window * max(n, m)))
        INF = np.inf

        # Allocate cost matrix
        D = np.full((n + 1, m + 1), INF)
        D[0, 0] = 0.0

        for i in range(1, n + 1):
            j_lo = max(1, i - w)
            j_hi = min(m, i + w)
            for j in range(j_lo, j_hi + 1):
                cost = (a[i - 1] - b[j - 1]) ** 2
                D[i, j] = cost + min(D[i - 1, j], D[i, j - 1], D[i - 1, j - 1])

        return float(np.sqrt(D[n, m]))
