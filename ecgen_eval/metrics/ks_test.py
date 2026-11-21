"""
Two-sample Kolmogorov–Smirnov test on signal features for ECG evaluation.

Reference
---------
Massey, F. J. (1951).
The Kolmogorov-Smirnov test for goodness of fit.
*Journal of the American Statistical Association*, 46(253), 68–78.
https://doi.org/10.1080/01621459.1951.10500769

Implementation notes
--------------------
Per lead:

1. Compute the 7-feature statistical descriptor of every recording (mean, std,
   RMS, max |x|, energy, zero-crossing rate, lag-1 autocorrelation).
2. For each feature, the two-sample KS statistic

     D = sup_x | F_real(x) − F_synth(x) |

   i.e. the largest gap between the two empirical distribution functions.
3. Lead score = mean D over the features.

The score is D (an effect size in [0, 1]), **not** a p-value: p-values shrink with
the sample size, so they are not comparable between runs with different N. p-values
are still reported in ``extra``, raw and adjusted for multiple testing over all
features × leads.
"""

from __future__ import annotations

from typing import List, Optional

import numpy as np

from ecgen_eval.metrics._matching import subsample
from ecgen_eval.metrics._signal_features import STAT_FEATURE_NAMES, stat_features
from ecgen_eval.metrics._stats import adjust_pvalues, ks_2samp, mann_whitney_pvalue
from ecgen_eval.metrics.base import BaseMetric, MetricResult

_REFERENCE = (
    "Massey, F. J. (1951). The Kolmogorov-Smirnov test for goodness of fit. Journal of the "
    "American Statistical Association, 46(253), 68–78. "
    "https://doi.org/10.1080/01621459.1951.10500769"
)

_DESCRIPTION = (
    "KS Test: mean two-sample Kolmogorov–Smirnov statistic between real and synthetic "
    "distributions of 7 signal features, per lead (p-values in extra). Lower is better."
)


class KSTestMetric(BaseMetric):
    """
    Mean two-sample KS statistic over 7 signal features, per lead.

    Parameters
    ----------
    n_subsample : int
        Max recordings per set. Default: 1000.
    alpha : float
        Significance level used for ``extra['n_rejected']``. Default: 0.05.
    correction : {'holm', 'bonferroni', 'none'}
        Multiple-testing adjustment over all features × leads. Default: 'holm'.
    seed : int
        Random seed. Default: 42.
    """

    name = "ks_test"
    description = _DESCRIPTION
    reference = _REFERENCE
    higher_is_better = False

    def __init__(
        self,
        n_subsample: int = 1000,
        alpha: float = 0.05,
        correction: str = "holm",
        seed: int = 42,
    ):
        if correction not in ("holm", "bonferroni", "none"):
            raise ValueError("correction must be 'holm', 'bonferroni' or 'none'.")
        self.n_subsample = n_subsample
        self.alpha = alpha
        self.correction = correction
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
        names = list(STAT_FEATURE_NAMES)
        n_feat = len(names)
        D = np.empty((n_leads, n_feat))
        P = np.empty((n_leads, n_feat))
        MWU = np.empty((n_leads, n_feat))
        p_method = "none"

        for li in range(n_leads):
            feats_r = stat_features(subsample(real[:, li, :], self.n_subsample, rng))
            feats_s = stat_features(subsample(synth[:, li, :], self.n_subsample, rng))
            for fi in range(n_feat):
                D[li, fi], P[li, fi], p_method = ks_2samp(feats_r[:, fi], feats_s[:, fi])
                MWU[li, fi] = mann_whitney_pvalue(feats_r[:, fi], feats_s[:, fi])

        P_adj = adjust_pvalues(P.ravel(), self.correction).reshape(P.shape)
        rejected = P_adj < self.alpha
        per_lead = {ln: float(np.mean(D[li])) for li, ln in enumerate(lead_names)}

        def table(arr: np.ndarray) -> dict:
            return {
                ln: {names[fi]: float(arr[li, fi]) for fi in range(n_feat)}
                for li, ln in enumerate(lead_names)
            }

        extra = {
            "feature_names": names,
            "per_lead_feature_D": table(D),
            "per_lead_feature_p": table(P),
            "per_lead_feature_p_adjusted": table(P_adj),
            "per_feature_D": {names[fi]: float(np.mean(D[:, fi])) for fi in range(n_feat)},
            "n_tests": int(D.size),
            "n_rejected": int(rejected.sum()),
            "frac_rejected": float(rejected.mean()),
            "alpha": self.alpha,
            "correction": self.correction,
            "p_method": p_method,
        }
        if np.isfinite(MWU).any():
            extra["per_lead_feature_mwu_p"] = table(MWU)

        return MetricResult(
            metric_name=self.name,
            score=float(np.mean(list(per_lead.values()))),
            higher_is_better=self.higher_is_better,
            per_lead_scores=per_lead,
            description=self.description,
            reference=self.reference,
            extra=extra,
        )
