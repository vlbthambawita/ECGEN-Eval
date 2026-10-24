"""
ECGEN-Eval: Evaluation metrics and interactive reports for synthetic ECG quality assessment.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    # Derived from the git tag at build time (hatch-vcs), e.g. v0.5.0 → "0.5.0".
    __version__ = version("ecgen-eval")
except PackageNotFoundError:  # running from a source tree that is not installed
    __version__ = "0.0.0+unknown"
__author__ = "Vajira Thambawita"

from ecgen_eval.data.loader import load_ecg_folder, load_ecg_npy, load_ecg_wfdb
from ecgen_eval.metrics import AVAILABLE_METRICS

__all__ = ["load_ecg_folder", "load_ecg_npy", "load_ecg_wfdb", "AVAILABLE_METRICS"]
