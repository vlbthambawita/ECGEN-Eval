"""
FeatureExtractor — runs a delineation backend and a selection of feature groups over an
ECGDataset and returns DataFrames.

Two independent choices:

- **backend** — the library that finds the beats and fiducials
  (:mod:`ecgen_eval.features.backends`: ``hybrid``, ``neurokit2``, ``scipy`` or your own).
- **features** — which feature groups / columns to compute
  (:mod:`ecgen_eval.features.groups`: ``rhythm``, ``intervals``, ``amplitude``, ``hrv`` or
  your own).
"""

from __future__ import annotations

import warnings
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

from ecgen_eval.data.dataset import ECGDataset
from ecgen_eval.features.backends import DelineationBackend, get_backend
from ecgen_eval.features.groups import (
    FeatureGroup,
    FeatureSpec,
    RecordingContext,
    resolve_features,
)


class FeatureExtractor:
    """
    Extract clinically meaningful ECG features from an ECGDataset.

    Parameters
    ----------
    lead_for_intervals : str
        Lead whose R peaks define the beats (RR/HR/HRV).  Defaults to "II"; if not
        present the first available lead is used.
    rpeak_method : str or None
        ``nk.ecg_peaks`` method (or ``"scipy"``) given to the backend.  None keeps the
        backend's default.
    delineation_method : str or None
        ``nk.ecg_delineate`` method given to the backend (``hybrid`` default
        ``"prominence"``, ``neurokit2`` default ``"dwt"``).  None keeps the backend's default.
    features : None, str, FeatureGroup, callable or a list of them
        What to compute: group names (``"rhythm"``, ``"intervals"``, ``"amplitude"``,
        ``"hrv"``), individual column names (e.g. ``"qtc_bazett_ms"``), ``FeatureGroup``
        instances or ``func(ctx) -> dict`` callables.  None / ``"all"`` computes every
        registered group.
    backend : str or DelineationBackend
        Delineation library: ``"hybrid"`` (default), ``"neurokit2"``, ``"scipy"``, any name
        added with ``register_backend``, or a backend instance.
    backend_kwargs : dict, optional
        Extra constructor arguments for a backend given by name.

    Outputs
    -------
    beat_df : pd.DataFrame
        One row per (sample_idx, beat_idx, lead).  Always has r_sample and rr_ms; plus the
        per-beat columns (intervals) and per-lead columns (amplitudes) of the selected groups.

    summary_df : pd.DataFrame
        One row per recording: ``sample_idx`` plus the selected feature columns.
    """

    def __init__(
        self,
        lead_for_intervals: str = "II",
        rpeak_method: Optional[str] = None,
        delineation_method: Optional[str] = None,
        features: Union[None, FeatureSpec, Iterable[FeatureSpec]] = None,
        backend: Union[str, DelineationBackend, None] = None,
        backend_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.lead_for_intervals = lead_for_intervals
        kwargs = dict(backend_kwargs or {})
        if rpeak_method is not None:
            kwargs["rpeak_method"] = rpeak_method
        if delineation_method is not None:
            kwargs["method"] = delineation_method
        self.backend = get_backend(backend, **kwargs)
        self.selection: List[Tuple[FeatureGroup, Optional[List[str]]]] = resolve_features(
            features
        )
        self._warned: set = set()

    @property
    def columns(self) -> List[str]:
        """Summary columns this extractor produces (unknown for groups without ``columns``)."""
        return [c for g, keep in self.selection for c in (keep or g.columns)]

    def __repr__(self) -> str:
        names = [g.name if keep is None else f"{g.name}{keep}" for g, keep in self.selection]
        return f"FeatureExtractor(backend={self.backend!r}, features={names})"

    # ---------------------------------------------------------------- #
    # Public API                                                         #
    # ---------------------------------------------------------------- #

    def extract(self, dataset: ECGDataset) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Run the feature extraction pipeline.

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
            ctx = self._delineate(dataset.data[sample_idx], dataset, primary_lead_idx)
            summary_rows.append(self._summary_row(ctx, sample_idx))
            beat_rows.extend(self._beat_rows(ctx, sample_idx))

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

    def _delineate(
        self, recording: np.ndarray, dataset: ECGDataset, primary_lead_idx: int
    ) -> RecordingContext:
        rec = np.asarray(recording, dtype=float)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                rpeaks, waves = self.backend.delineate(rec, dataset.fs, primary_lead_idx)
            except ImportError:
                raise
            except Exception as exc:  # flat / too short recording
                self._warn_once(self.backend, f"delineation failed ({exc})")
                rpeaks, waves = np.array([], dtype=int), None
        return RecordingContext(
            recording=rec,
            lead_names=list(dataset.lead_names),
            fs=dataset.fs,
            primary_lead_idx=primary_lead_idx,
            rpeaks=np.asarray(rpeaks, dtype=int),
            waves=waves,
        )

    def _summary_row(self, ctx: RecordingContext, sample_idx: int) -> dict:
        row = {"sample_idx": sample_idx}
        for group, keep in self.selection:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    values = group.compute(ctx)
            except Exception as exc:
                self._warn_once(group, f"failed ({exc}); its features are NaN")
                values = {c: np.nan for c in group.columns}
            cols = keep if keep is not None else (group.columns or list(values))
            row.update({c: values.get(c, np.nan) for c in cols})
        return row

    def _beat_rows(self, ctx: RecordingContext, sample_idx: int) -> List[dict]:
        per_beat: Dict[str, np.ndarray] = {}
        per_lead: Dict[str, np.ndarray] = {}
        for group, keep in self.selection:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    pb, pl = group.per_beat(ctx), group.per_lead(ctx)
            except Exception as exc:
                self._warn_once(group, f"per-beat values failed ({exc})")
                continue
            per_beat.update({k: v for k, v in pb.items() if keep is None or k in keep})
            per_lead.update({k: v for k, v in pl.items() if keep is None or k in keep})

        rpeaks = ctx.rpeaks
        rr_ms = np.diff(rpeaks.astype(float)) / ctx.fs * 1000.0 if len(rpeaks) >= 2 else []
        rows = []
        for lead_idx, lead_name in enumerate(ctx.lead_names):
            for beat_idx, (r, rr) in enumerate(zip(rpeaks, rr_ms)):
                rows.append(
                    {
                        "sample_idx": sample_idx,
                        "beat_idx": beat_idx,
                        "lead": lead_name,
                        "r_sample": int(r),
                        "rr_ms": float(rr),
                        **{k: float(v[beat_idx]) if beat_idx < len(v) else np.nan
                           for k, v in per_beat.items()},
                        **{k: float(v[lead_idx]) if lead_idx < len(v) else np.nan
                           for k, v in per_lead.items()},
                    }
                )
        return rows

    def _warn_once(self, owner, message: str) -> None:
        key = (getattr(owner, "name", repr(owner)), message.split(" (")[0])
        if key not in self._warned:
            self._warned.add(key)
            warnings.warn(f"{owner!r}: {message}", RuntimeWarning, stacklevel=3)


# ------------------------------------------------------------------ #
# Convenience function                                                 #
# ------------------------------------------------------------------ #

def extract_features(
    dataset: ECGDataset,
    lead_for_intervals: str = "II",
    features: Union[None, FeatureSpec, Iterable[FeatureSpec]] = None,
    backend: Union[str, DelineationBackend, None] = None,
    **kwargs,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Convenience wrapper around :class:`FeatureExtractor`.

    Extra keyword arguments (``rpeak_method``, ``delineation_method``, ``backend_kwargs``)
    are passed to :class:`FeatureExtractor`.

    Returns
    -------
    (beat_df, summary_df)
    """
    extractor = FeatureExtractor(
        lead_for_intervals=lead_for_intervals, features=features, backend=backend, **kwargs
    )
    return extractor.extract(dataset)
