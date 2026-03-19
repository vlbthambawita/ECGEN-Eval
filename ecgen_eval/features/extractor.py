"""
FeatureExtractor — wires QRS detection, interval, amplitude, and HRV modules
into a unified pipeline that accepts an ECGDataset and returns DataFrames.
"""

from __future__ import annotations

import warnings
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd

from ecgen_eval.data.dataset import ECGDataset
from ecgen_eval.features.qrs_detection import detect_rpeaks, delineate_ecg
from ecgen_eval.features.interval_features import extract_rr_hr, extract_interval_features
from ecgen_eval.features.amplitude_features import extract_amplitude_features
from ecgen_eval.features.hrv_features import extract_hrv_features


class FeatureExtractor:
    """
    Extract clinically meaningful ECG features from an ECGDataset.

    Parameters
    ----------
    lead_for_intervals : str
        Lead used for RR/HR/HRV and interval timing.  Defaults to "II"; if not
        present the first available lead is used.
    rpeak_method : str
        Passed to neurokit2.ecg_peaks().  Ignored when neurokit2 absent.

    Outputs
    -------
    beat_df : pd.DataFrame
        One row per (recording_idx, beat_idx, lead_name).
        Columns: rr_ms, t_amplitude_mv, st_deviation_mv.

    summary_df : pd.DataFrame
        One row per recording.  Columns: rr_mean_ms, rr_std_ms, hr_bpm,
        pr_interval_ms, qrs_duration_ms, qt_interval_ms, qtc_bazett_ms,
        p_wave_duration_ms, hrv_sdnn_ms, hrv_rmssd_ms, hrv_pnn50,
        st_deviation_mv, t_amplitude_mv  (amplitude averaged over all leads).
    """

    def __init__(
        self,
        lead_for_intervals: str = "II",
        rpeak_method: str = "neurokit",
    ) -> None:
        self.lead_for_intervals = lead_for_intervals
        self.rpeak_method = rpeak_method

    # ---------------------------------------------------------------- #
    # Public API                                                         #
    # ---------------------------------------------------------------- #

    def extract(self, dataset: ECGDataset) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Run the full feature extraction pipeline.

        Parameters
        ----------
        dataset : ECGDataset  — shape (N, L, T).

        Returns
        -------
        (beat_df, summary_df)
        """
        beat_rows: List[dict] = []
        summary_rows: List[dict] = []

        primary_lead_idx = self._primary_lead_idx(dataset.lead_names)

        for sample_idx in range(dataset.n_samples):
            recording = dataset.data[sample_idx]  # (L, T)
            row = self._extract_one(
                recording=recording,
                lead_names=dataset.lead_names,
                fs=dataset.fs,
                primary_lead_idx=primary_lead_idx,
                sample_idx=sample_idx,
                beat_rows=beat_rows,
            )
            summary_rows.append(row)

        beat_df = pd.DataFrame(beat_rows)
        summary_df = pd.DataFrame(summary_rows)
        return beat_df, summary_df

    # ---------------------------------------------------------------- #
    # Internal helpers                                                   #
    # ---------------------------------------------------------------- #

    def _primary_lead_idx(self, lead_names: List[str]) -> int:
        if self.lead_for_intervals in lead_names:
            return lead_names.index(self.lead_for_intervals)
        return 0  # fallback to first lead

    def _extract_one(
        self,
        recording: np.ndarray,
        lead_names: List[str],
        fs: float,
        primary_lead_idx: int,
        sample_idx: int,
        beat_rows: List[dict],
    ) -> dict:
        """Process one recording (L, T) → summary feature dict."""

        primary_sig = recording[primary_lead_idx].astype(float)

        # ---- R-peak detection on primary lead ----
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            rpeaks = detect_rpeaks(primary_sig, fs, method=self.rpeak_method)

        # ---- Delineation on primary lead (neurokit2 if available) ----
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            waves = delineate_ecg(primary_sig, rpeaks, fs)

        # ---- RR / HR ----
        rr_hr = extract_rr_hr(rpeaks, fs)

        # ---- Interval features (primary lead) ----
        interval_feats = extract_interval_features(primary_sig, fs, rpeaks, waves)

        # ---- HRV (primary lead) ----
        hrv_feats = extract_hrv_features(rpeaks, fs)

        # ---- Amplitude features (all leads, then average) ----
        st_vals, t_vals = [], []
        rr_ms_series = (
            np.diff(rpeaks.astype(float)) / fs * 1000.0 if len(rpeaks) >= 2 else np.array([])
        )

        for lead_idx, lead_name in enumerate(lead_names):
            lead_sig = recording[lead_idx].astype(float)
            amp = extract_amplitude_features(lead_sig, fs, rpeaks, waves)
            st_vals.append(amp["st_deviation_mv"])
            t_vals.append(amp["t_amplitude_mv"])

            # Beat-level rows for this lead
            for beat_idx, (r, rr) in enumerate(zip(rpeaks, rr_ms_series)):
                beat_rows.append(
                    {
                        "sample_idx": sample_idx,
                        "beat_idx": beat_idx,
                        "lead": lead_name,
                        "r_sample": int(r),
                        "rr_ms": float(rr),
                        "st_deviation_mv": amp["st_deviation_mv"],
                        "t_amplitude_mv": amp["t_amplitude_mv"],
                    }
                )

        st_mean = float(np.nanmean(st_vals)) if any(np.isfinite(v) for v in st_vals) else np.nan
        t_mean = float(np.nanmean(t_vals)) if any(np.isfinite(v) for v in t_vals) else np.nan

        return {
            "sample_idx": sample_idx,
            **rr_hr,
            **interval_feats,
            **hrv_feats,
            "st_deviation_mv": st_mean,
            "t_amplitude_mv": t_mean,
        }


# ------------------------------------------------------------------ #
# Convenience function                                                 #
# ------------------------------------------------------------------ #

def extract_features(
    dataset: ECGDataset,
    lead_for_intervals: str = "II",
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Convenience wrapper around :class:`FeatureExtractor`.

    Returns
    -------
    (beat_df, summary_df)
    """
    extractor = FeatureExtractor(lead_for_intervals=lead_for_intervals)
    return extractor.extract(dataset)
