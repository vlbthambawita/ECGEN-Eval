"""
ecgen_eval.features — Clinical ECG feature extraction subpackage.

Primary exports
---------------
FeatureExtractor : class
    Full pipeline: ECGDataset → (beat_df, summary_df).
extract_features : function
    Convenience wrapper around FeatureExtractor.

Customisation
-------------
Choose *what* to compute with ``features=`` (group or column names, ``FeatureGroup``
instances or ``func(ctx) -> dict`` callables) and *which library* delineates the beats with
``backend=`` (``"hybrid"``, ``"neurokit2"``, ``"scipy"``). Extend either registry with
``register_feature_group`` / ``feature_group`` and ``register_backend``.

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

from ecgen_eval.features.backends import (
    AVAILABLE_BACKENDS,
    DelineationBackend,
    HybridBackend,
    NeuroKitBackend,
    ScipyBackend,
    get_backend,
    register_backend,
)
from ecgen_eval.features.extractor import FeatureExtractor, extract_features
from ecgen_eval.features.groups import (
    AVAILABLE_FEATURE_GROUPS,
    FeatureGroup,
    FunctionFeatureGroup,
    RecordingContext,
    available_features,
    feature_group,
    register_feature_group,
)

__all__ = [
    "FeatureExtractor",
    "extract_features",
    "AVAILABLE_BACKENDS",
    "DelineationBackend",
    "HybridBackend",
    "NeuroKitBackend",
    "ScipyBackend",
    "get_backend",
    "register_backend",
    "AVAILABLE_FEATURE_GROUPS",
    "FeatureGroup",
    "FunctionFeatureGroup",
    "RecordingContext",
    "available_features",
    "feature_group",
    "register_feature_group",
]
