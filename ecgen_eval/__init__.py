"""
ECGEN-Eval: Evaluation metrics and interactive reports for synthetic ECG quality assessment.
"""

__version__ = "0.1.0"
__author__ = "Vajira Thambawita"

from ecgen_eval.data.loader import load_ecg_folder, load_ecg_npy, load_ecg_wfdb
from ecgen_eval.metrics import AVAILABLE_METRICS

__all__ = ["load_ecg_folder", "load_ecg_npy", "load_ecg_wfdb", "AVAILABLE_METRICS"]
