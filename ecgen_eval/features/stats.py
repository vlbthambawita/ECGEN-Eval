"""Statistical comparison of clinical-feature distributions (real vs. synthetic)."""

from __future__ import annotations

from typing import List, Optional

import numpy as np
import pandas as pd

from ecgen_eval.metrics._stats import adjust_pvalues, cohens_d, ks_2samp, mann_whitney_pvalue

_SKIP_COLUMNS = {"sample_idx", "beat_idx", "lead", "r_sample"}


def compare_feature_distributions(
    real_df: pd.DataFrame,
    synth_df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    correction: str = "holm",
) -> pd.DataFrame:
    """
    Two-sample tests between real and synthetic clinical-feature distributions.

    Parameters
    ----------
    real_df, synth_df : summary DataFrames from ``FeatureExtractor.extract`` (one row
        per recording)
    columns : features to test. Default: every numeric column present in both.
    correction : 'holm' (default), 'bonferroni' or 'none' — multiple-testing
        adjustment of the KS p-values over the tested features

    Returns
    -------
    DataFrame with one row per feature and the columns

    ``feature``, ``n_real``, ``n_synth`` (rows without NaN), ``ks_D`` (two-sample
    Kolmogorov–Smirnov statistic, 0 = same distribution, 1 = no overlap), ``ks_p``,
    ``ks_p_adjusted``, ``mwu_p`` (Mann–Whitney U, NaN without SciPy) and
    ``cohens_d`` ((mean synthetic − mean real) / pooled SD).

    Read ``ks_D`` and ``cohens_d`` as effect sizes. p-values shrink with the number
    of recordings, so with large sets even negligible differences are "significant".
    """
    if columns is None:
        columns = [
            c for c in real_df.columns
            if c not in _SKIP_COLUMNS and c in synth_df.columns
            and pd.api.types.is_numeric_dtype(real_df[c])
            and pd.api.types.is_numeric_dtype(synth_df[c])
        ]
    rows = []
    for col in columns:
        a = real_df[col].to_numpy(dtype=np.float64)
        b = synth_df[col].to_numpy(dtype=np.float64)
        a, b = a[~np.isnan(a)], b[~np.isnan(b)]
        d, p, _ = ks_2samp(a, b)
        rows.append({
            "feature": col,
            "n_real": int(a.size),
            "n_synth": int(b.size),
            "ks_D": d,
            "ks_p": p,
            "mwu_p": mann_whitney_pvalue(a, b),
            "cohens_d": cohens_d(a, b),
        })
    out = pd.DataFrame(
        rows, columns=["feature", "n_real", "n_synth", "ks_D", "ks_p", "mwu_p", "cohens_d"]
    )
    out.insert(5, "ks_p_adjusted", adjust_pvalues(out["ks_p"].to_numpy(), correction))
    return out
