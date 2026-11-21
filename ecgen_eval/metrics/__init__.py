from ecgen_eval.metrics.mmd import MMDMetric
from ecgen_eval.metrics.fed import FEDMetric
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
from ecgen_eval.metrics.mse import MSEMetric, RMSEMetric
from ecgen_eval.metrics.pearson import PearsonMetric
from ecgen_eval.metrics.cosine import CosineMetric
from ecgen_eval.metrics.euclidean import EuclideanMetric
from ecgen_eval.metrics.curve_frechet import CurveFrechetMetric
from ecgen_eval.metrics.js_div import AmplitudeJSMetric
from ecgen_eval.metrics.ks_test import KSTestMetric
from ecgen_eval.metrics.c2st import C2STMetric

AVAILABLE_METRICS = {
    # --- Original metrics ---
    "mmd":              MMDMetric,
    "dtw":              DTWMetric,
    "prd":              PRDMetric,
    "psd":              PSDMetric,
    "fd":               FDMetric,
    "fed":              FEDMetric,
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
    # --- Fidelity metrics used in more than 10 papers of the literature review ---
    "mse":              MSEMetric,
    "rmse":             RMSEMetric,
    "pearson":          PearsonMetric,
    "cosine":           CosineMetric,
    "euclidean":        EuclideanMetric,
    "curve_frechet":    CurveFrechetMetric,
    "js_div":           AmplitudeJSMetric,
    "ks_test":          KSTestMetric,
    "c2st":             C2STMetric,
}

__all__ = [
    "MMDMetric", "DTWMetric", "PRDMetric", "PSDMetric", "FDMetric", "FEDMetric",
    "PSNRMetric", "SSIMMetric", "SWDMetric", "MAEMetric", "HRVMetric",
    "PRDistMetric", "SQIMetric", "NNDistMetric", "HeartRateMetric",
    "SpectralEntropyMetric",
    "MSEMetric", "RMSEMetric", "PearsonMetric", "CosineMetric", "EuclideanMetric",
    "CurveFrechetMetric", "AmplitudeJSMetric", "KSTestMetric", "C2STMetric",
    "AVAILABLE_METRICS",
]
