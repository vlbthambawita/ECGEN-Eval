"""
ecgen_eval.features — Clinical ECG feature extraction subpackage.

Primary exports
---------------
FeatureExtractor : class
    Full pipeline: ECGDataset → (beat_df, summary_df).
extract_features : function
    Convenience wrapper around FeatureExtractor.

Optional dependency
-------------------
``neurokit2`` is used for R-peak detection and full waveform delineation.
Install with::

    pip install neurokit2
    # or
    pip install "ecgen-eval[features]"

If neurokit2 is absent the package falls back to a scipy-based Pan-Tompkins
implementation and heuristic interval estimates.
"""

from ecgen_eval.features.extractor import FeatureExtractor, extract_features

__all__ = ["FeatureExtractor", "extract_features"]
