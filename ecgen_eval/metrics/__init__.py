from ecgen_eval.metrics.mmd import MMDMetric
from ecgen_eval.metrics.dtw import DTWMetric
from ecgen_eval.metrics.prd import PRDMetric
from ecgen_eval.metrics.psd import PSDMetric
from ecgen_eval.metrics.fd import FDMetric
from ecgen_eval.metrics.psnr import PSNRMetric
from ecgen_eval.metrics.ssim import SSIMMetric
from ecgen_eval.metrics.swd import SWDMetric
from ecgen_eval.metrics.mae import MAEMetric
from ecgen_eval.metrics.hrv import HRVMetric
from ecgen_eval.metrics.pr_dist import PRDistMetric
from ecgen_eval.metrics.sqi import SQIMetric
from ecgen_eval.metrics.nn_dist import NNDistMetric
from ecgen_eval.metrics.heart_rate import HeartRateMetric
from ecgen_eval.metrics.spectral_entropy import SpectralEntropyMetric

AVAILABLE_METRICS = {
    # --- Original metrics ---
    "mmd":              MMDMetric,
    "dtw":              DTWMetric,
    "prd":              PRDMetric,
    "psd":              PSDMetric,
    "fd":               FDMetric,
    # --- New metrics ---
    "psnr":             PSNRMetric,
    "ssim":             SSIMMetric,
    "swd":              SWDMetric,
    "mae":              MAEMetric,
    "hrv":              HRVMetric,
    "pr_dist":          PRDistMetric,
    "sqi":              SQIMetric,
    "nn_dist":          NNDistMetric,
    "heart_rate":       HeartRateMetric,
    "spectral_entropy": SpectralEntropyMetric,
}

__all__ = [
    "MMDMetric", "DTWMetric", "PRDMetric", "PSDMetric", "FDMetric",
    "PSNRMetric", "SSIMMetric", "SWDMetric", "MAEMetric", "HRVMetric",
    "PRDistMetric", "SQIMetric", "NNDistMetric", "HeartRateMetric",
    "SpectralEntropyMetric",
    "AVAILABLE_METRICS",
]
