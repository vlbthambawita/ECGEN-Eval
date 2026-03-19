"""Abstract base class for all ECGEN-Eval metrics."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np


@dataclass
class MetricResult:
    """
    Standardised result returned by every metric.

    Attributes
    ----------
    metric_name : str
        Short identifier (e.g. "mmd", "dtw").
    score : float
        Primary scalar score. Convention: lower = more similar to real data,
        unless ``higher_is_better`` is True.
    higher_is_better : bool
        If True, a higher score means better quality.
    per_lead_scores : dict
        Optional per-lead breakdown {lead_name: score}.
    extra : dict
        Any additional data the metric wants to expose (e.g. p-values,
        per-sample distances) for rich report rendering.
    description : str
        One-line human-readable description of what was measured.
    reference : str
        Citation for the metric.
    """

    metric_name: str
    score: float
    higher_is_better: bool = False
    per_lead_scores: Dict[str, float] = field(default_factory=dict)
    extra: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    reference: str = ""

    def summary_dict(self) -> Dict[str, Any]:
        return {
            "metric": self.metric_name,
            "score": round(self.score, 6),
            "higher_is_better": self.higher_is_better,
            "per_lead_scores": {k: round(v, 6) for k, v in self.per_lead_scores.items()},
        }


class BaseMetric(ABC):
    """
    Abstract base class all metrics must inherit from.

    Subclasses implement :meth:`compute` which receives two arrays:
    - ``real``  : np.ndarray of shape (N_r, L, T)
    - ``synth`` : np.ndarray of shape (N_s, L, T)

    and returns a :class:`MetricResult`.
    """

    #: Short key used in CLI and reports (e.g. "mmd")
    name: str = ""
    #: One-line description shown in report
    description: str = ""
    #: Full citation
    reference: str = ""
    #: True if higher score = better
    higher_is_better: bool = False

    @abstractmethod
    def compute(
        self,
        real: np.ndarray,
        synth: np.ndarray,
        lead_names: Optional[List[str]] = None,
    ) -> MetricResult:
        """
        Compute the metric.

        Parameters
        ----------
        real : np.ndarray  shape (N_r, L, T)
        synth : np.ndarray shape (N_s, L, T)
        lead_names : list of str, optional

        Returns
        -------
        MetricResult
        """
        ...

    def _check_inputs(self, real: np.ndarray, synth: np.ndarray) -> None:
        if real.ndim != 3 or synth.ndim != 3:
            raise ValueError(
                f"Expected 3-D arrays (N, L, T), got real={real.shape}, synth={synth.shape}"
            )
        if real.shape[1] != synth.shape[1]:
            raise ValueError(
                f"Lead count mismatch: real has {real.shape[1]}, synth has {synth.shape[1]}"
            )
