from ecgen_eval.metrics.mmd import MMDMetric
from ecgen_eval.metrics.dtw import DTWMetric
from ecgen_eval.metrics.prd import PRDMetric
from ecgen_eval.metrics.psd import PSDMetric
from ecgen_eval.metrics.fd import FDMetric

AVAILABLE_METRICS = {
    "mmd": MMDMetric,
    "dtw": DTWMetric,
    "prd": PRDMetric,
    "psd": PSDMetric,
    "fd":  FDMetric,
}

__all__ = ["MMDMetric", "DTWMetric", "PRDMetric", "PSDMetric", "FDMetric", "AVAILABLE_METRICS"]
