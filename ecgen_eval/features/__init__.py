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
``neurokit2`` is used for R-peak detection and P/T-wave delineation; QRS boundaries come
from the spatial velocity of all leads (see ``ecgen_eval.features.delineation``).
Install with::

    pip install neurokit2
    # or
    pip install "ecgen-eval[features]"

If neurokit2 is absent the package falls back to a scipy-based Pan-Tompkins
detector; features that need P/T boundaries (PR, QT, QTc, P duration) are then NaN.
"""

from ecgen_eval.features.extractor import FeatureExtractor, extract_features

__all__ = ["FeatureExtractor", "extract_features"]
