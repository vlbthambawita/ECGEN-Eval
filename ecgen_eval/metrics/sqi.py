"""
Signal Quality Index (SQI) via QRS Template Correlation for ECG evaluation.

Reference
---------
Clifford, G. D., et al. (2012).
AF classification from a short single lead ECG recording: the PhysioNet/
Computing in Cardiology Challenge 2017.
*Computing in Cardiology*, 44, 1–4.
https://doi.org/10.22489/CinC.2017.065-469

Johnson, A. E., et al. (2015).
The MIMIC Code Repository: enabling reproducibility in critical care
research.
*Journal of the American Medical Informatics Association*, 23(1), 127–135.
https://doi.org/10.1093/jamia/ocv050

Implementation notes
--------------------
A per-lead QRS template is built by averaging all real ECG recordings
(each amplitude-normalised to unit range).  For each synthetic recording
the Pearson correlation with the real template is computed.

  SQI = (1/N_s) · Σ corr(synthetic_i_normalised, template)

Range: [-1, 1].  A score near 1 indicates that the synthetic ECGs have
the same gross morphology as the real template; lower values indicate
divergent waveform shapes or opposite polarity.  Higher is better.
"""

from __future__ import annotations

from typing import List, Optional

import numpy as np

from ecgen_eval.metrics.base import BaseMetric, MetricResult


_REFERENCE = (
    "Clifford, G. D., et al. (2012). AF classification from a short single lead ECG recording: "
    "the PhysioNet/Computing in Cardiology Challenge 2017. "
    "Computing in Cardiology, 44, 1–4. https://doi.org/10.22489/CinC.2017.065-469"
)

_DESCRIPTION = (
    "Signal Quality Index (SQI): mean Pearson correlation between synthetic ECGs and the "
    "real-ECG QRS morphology template. Range [-1, 1]; higher is better."
)


class SQIMetric(BaseMetric):
    """
    Template-correlation SQI per lead.

    Parameters
    ----------
    n_subsample : int
        Max samples per lead. Default: 1000.
    seed : int
        Random seed. Default: 42.
    """

    name = "sqi"
    description = _DESCRIPTION
    reference = _REFERENCE
    higher_is_better = True

    def __init__(self, n_subsample: int = 1000, seed: int = 42):
        self.n_subsample = n_subsample
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
        real_baseline: dict = {}

        for li, lname in enumerate(lead_names):
            real_l = real[:, li, :]    # (Nr, T)
            synth_l = synth[:, li, :]  # (Ns, T)

            real_l_sub = self._subsample(real_l, rng)
            synth_l_sub = self._subsample(synth_l, rng)

            # Build template from real (mean of normalised signals)
            real_norm = self._normalise(real_l_sub)
            template = real_norm.mean(axis=0)

            # Correlate each synthetic against the template
            synth_norm = self._normalise(synth_l_sub)
            corr_vals = [self._pearson(synth_norm[i], template) for i in range(len(synth_norm))]

            # Baseline: correlate real against own template
            real_corr = [self._pearson(real_norm[i], template) for i in range(len(real_norm))]

            per_lead[lname] = float(np.mean(corr_vals))
            real_baseline[lname] = float(np.mean(real_corr))

        score = float(np.mean(list(per_lead.values())))
        return MetricResult(
            metric_name=self.name,
            score=score,
            higher_is_better=self.higher_is_better,
            per_lead_scores=per_lead,
            description=self.description,
            reference=self.reference,
            extra={"real_self_sqi": real_baseline},
        )

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _normalise(X: np.ndarray) -> np.ndarray:
        """Amplitude-normalise each row to zero mean, unit range."""
        X = X - X.mean(axis=1, keepdims=True)
        rng = np.ptp(X, axis=1, keepdims=True)
        rng = np.where(rng < 1e-9, 1.0, rng)
        return X / rng

    @staticmethod
    def _pearson(a: np.ndarray, b: np.ndarray) -> float:
        a_c = a - a.mean()
        b_c = b - b.mean()
        denom = np.sqrt(np.dot(a_c, a_c) * np.dot(b_c, b_c)) + 1e-15
        return float(np.dot(a_c, b_c) / denom)

    def _subsample(self, X: np.ndarray, rng: np.random.Generator) -> np.ndarray:
        if X.shape[0] <= self.n_subsample:
            return X
        idx = rng.choice(X.shape[0], size=self.n_subsample, replace=False)
        return X[idx]
