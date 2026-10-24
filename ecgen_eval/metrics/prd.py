"""
Percent Root-mean-square Difference (PRD) metric.

Reference
---------
Zigel, Y., Cohen, A., & Katsevman, A. (2000).
The weighted diagnostic distortion (WDD) measure for ECG signal compression.
*IEEE Transactions on Biomedical Engineering*, 47(11), 1422–1430.
https://doi.org/10.1109/10.871205

Also used in:
  Thambawita, V., et al. (2021). DeepFake electrocardiograms using generative
  adversarial networks are the beginning of the end for privacy issues in medicine.
  *Scientific Reports*, 11, 21896. https://doi.org/10.1038/s41598-021-01295-2

Implementation notes
--------------------
PRD measures the percentage distortion of a synthetic signal relative to a real
reference.  For generative models (unpaired evaluation) we compute PRD between
each real signal and its *nearest synthetic neighbour* (by Euclidean distance
in the flattened lead space), then average across the real set.

  PRD(x_real, x_synth) = 100 × ‖x_real − x_synth‖₂ / ‖x_real‖₂

per lead; the overall score is the mean across leads.
"""

from __future__ import annotations

from typing import List, Optional

import numpy as np

from ecgen_eval.metrics.base import BaseMetric, MetricResult


_REFERENCE = (
    "Zigel, Y., Cohen, A., & Katsevman, A. (2000). The weighted diagnostic distortion "
    "measure for ECG signal compression. IEEE Transactions on Biomedical Engineering, "
    "47(11), 1422–1430. https://doi.org/10.1109/10.871205"
)

_DESCRIPTION = (
    "Percent Root-mean-square Difference (PRD): measures waveform distortion of the "
    "nearest synthetic neighbour for each real ECG. "
    "PRD = 100 × ‖real − synth‖₂ / ‖real‖₂ (%). Lower is better."
)


class PRDMetric(BaseMetric):
    """
    PRD computed per lead between each real recording and its nearest synthetic
    neighbour in the flattened feature space, averaged over real samples.

    Parameters
    ----------
    n_subsample : int
        Cap on number of real/synthetic samples used (for speed). Default: 500.
    seed : int
        Random seed when subsampling.
    """

    name = "prd"
    description = _DESCRIPTION
    reference = _REFERENCE
    higher_is_better = False

    def __init__(self, n_subsample: int = 500, seed: int = 42):
        self.n_subsample = n_subsample
        self.seed = seed

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
        r = real if real.shape[0] <= self.n_subsample else real[
            rng.choice(real.shape[0], self.n_subsample, replace=False)]
        s = synth if synth.shape[0] <= self.n_subsample else synth[
            rng.choice(synth.shape[0], self.n_subsample, replace=False)]

        # For each real signal find nearest synthetic via flattened Euclidean distance
        # Compute per-lead PRD for those pairs
        r_flat = r.reshape(r.shape[0], -1).astype(np.float64)  # (Nr, L*T)
        s_flat = s.reshape(s.shape[0], -1).astype(np.float64)  # (Ns, L*T)

        # argmin_s ‖r − s‖² = argmin_s (‖s‖² − 2·r·s); ‖r‖² is constant per row.
        # Uses an (Nr, Ns) matrix instead of an (Nr, Ns, L*T) difference tensor.
        s_sq = np.einsum("ij,ij->i", s_flat, s_flat)        # (Ns,)
        sq_dist = s_sq[None, :] - 2.0 * (r_flat @ s_flat.T)  # (Nr, Ns), up to a row constant
        nn_idx = np.argmin(sq_dist, axis=1)                  # (Nr,)

        nn_synth = s[nn_idx]  # (Nr, L, T)

        per_lead: dict = {}
        for li, lname in enumerate(lead_names):
            r_lead = r[:, li, :]          # (Nr, T)
            s_lead = nn_synth[:, li, :]   # (Nr, T)
            num = np.sqrt(np.sum((r_lead - s_lead) ** 2, axis=-1))
            den = np.sqrt(np.sum(r_lead ** 2, axis=-1)) + 1e-9
            prd_per_sample = 100.0 * num / den
            per_lead[lname] = float(np.mean(prd_per_sample))

        overall = float(np.mean(list(per_lead.values())))

        return MetricResult(
            metric_name=self.name,
            score=overall,
            higher_is_better=self.higher_is_better,
            per_lead_scores=per_lead,
            description=self.description,
            reference=self.reference,
        )
