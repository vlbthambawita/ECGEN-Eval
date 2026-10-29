"""
Feature groups: what is measured from a delineated recording.

A feature group computes a few related ``summary_df`` columns from a
:class:`RecordingContext` (the recording plus the R peaks and fiducials found by the
delineation backend). Groups can also add per-beat or per-lead columns to ``beat_df``.

Built-in groups
---------------
==============  ==============================================================================
``rhythm``      ``rr_mean_ms``, ``rr_std_ms``, ``hr_bpm``
``intervals``   ``pr_interval_ms``, ``qrs_duration_ms``, ``qt_interval_ms``, ``qtc_bazett_ms``,
                ``p_wave_duration_ms``
``hrv``         ``hrv_sdnn_ms``, ``hrv_rmssd_ms``, ``hrv_pnn50``
``amplitude``   ``st_deviation_mv``, ``t_amplitude_mv``
==============  ==============================================================================

Add your own by subclassing :class:`FeatureGroup`, or decorate a function with
:func:`feature_group`::

    @feature_group("qrs_energy", columns=["qrs_energy"])
    def qrs_energy(ctx):
        return {"qrs_energy": float(np.sum(ctx.primary_signal ** 2))}
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple, Union

import numpy as np

from ecgen_eval.features.amplitude_features import extract_amplitude_features
from ecgen_eval.features.hrv_features import extract_hrv_features
from ecgen_eval.features.interval_features import (
    beat_intervals,
    extract_interval_features,
    extract_rr_hr,
)


@dataclass
class RecordingContext:
    """Everything a feature group may use for one recording."""

    recording: np.ndarray            # (L, T)
    lead_names: List[str]
    fs: float
    primary_lead_idx: int
    rpeaks: np.ndarray               # (M,) R-peak sample indices on the primary lead
    waves: Optional[Dict[str, np.ndarray]]  # fiducials aligned with rpeaks, or None
    cache: dict = field(default_factory=dict)  # scratch space shared by groups

    @property
    def primary_signal(self) -> np.ndarray:
        return self.recording[self.primary_lead_idx].astype(float)

    @property
    def n_beats(self) -> int:
        return len(self.rpeaks)


class FeatureGroup:
    """
    Base class for a group of related features.

    Subclasses set ``name``, ``columns`` and ``description`` and implement :meth:`compute`.
    :meth:`per_beat` / :meth:`per_lead` optionally add columns to ``beat_df``.
    """

    name: str = ""
    columns: Tuple[str, ...] = ()
    description: str = ""

    def compute(self, ctx: RecordingContext) -> Dict[str, float]:
        """Summary values for one recording, keyed by column name."""
        raise NotImplementedError

    def per_beat(self, ctx: RecordingContext) -> Dict[str, np.ndarray]:
        """Arrays of length ``ctx.n_beats`` (one value per beat, shared by all leads)."""
        return {}

    def per_lead(self, ctx: RecordingContext) -> Dict[str, np.ndarray]:
        """Arrays of length ``len(ctx.lead_names)`` (one value per lead, shared by beats)."""
        return {}

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self.name!r})"


class RhythmFeatures(FeatureGroup):
    name = "rhythm"
    columns = ("rr_mean_ms", "rr_std_ms", "hr_bpm")
    description = "RR interval mean/std and heart rate from the primary-lead R peaks"

    def compute(self, ctx):
        return extract_rr_hr(ctx.rpeaks, ctx.fs)


class IntervalFeatures(FeatureGroup):
    name = "intervals"
    columns = ("pr_interval_ms", "qrs_duration_ms", "qt_interval_ms", "qtc_bazett_ms",
               "p_wave_duration_ms")
    description = "PR, QRS, QT, QTc (Bazett) and P-wave duration; median over beats"

    def compute(self, ctx):
        if ctx.waves is None:
            return {c: np.nan for c in self.columns}
        return extract_interval_features(ctx.recording, ctx.fs, ctx.rpeaks, ctx.waves)

    def per_beat(self, ctx):
        return beat_intervals(ctx.waves, ctx.fs)


class AmplitudeFeatures(FeatureGroup):
    name = "amplitude"
    columns = ("st_deviation_mv", "t_amplitude_mv")
    description = "ST deviation (J+80 ms) and signed T amplitude per lead, averaged over leads"

    def _lead_values(self, ctx) -> Dict[str, np.ndarray]:
        if "amplitude" not in ctx.cache:
            vals = {c: [] for c in self.columns}
            for lead in ctx.recording:
                amp = (extract_amplitude_features(lead.astype(float), ctx.fs, ctx.rpeaks,
                                                  ctx.waves)
                       if ctx.waves is not None else {c: np.nan for c in self.columns})
                for c in self.columns:
                    vals[c].append(amp[c])
            ctx.cache["amplitude"] = {c: np.asarray(v, dtype=float) for c, v in vals.items()}
        return ctx.cache["amplitude"]

    def compute(self, ctx):
        out = {}
        for c, v in self._lead_values(ctx).items():
            out[c] = float(np.nanmean(v)) if np.isfinite(v).any() else np.nan
        return out

    def per_lead(self, ctx):
        return self._lead_values(ctx)


class HRVFeatures(FeatureGroup):
    name = "hrv"
    columns = ("hrv_sdnn_ms", "hrv_rmssd_ms", "hrv_pnn50")
    description = "Time-domain HRV: SDNN, RMSSD, pNN50"

    def compute(self, ctx):
        return extract_hrv_features(ctx.rpeaks, ctx.fs)


class FunctionFeatureGroup(FeatureGroup):
    """
    Wrap a plain function ``func(ctx) -> dict`` as a feature group.

    ``columns`` may be omitted; individual columns of such a group can then not be selected
    by name, but the group can.
    """

    def __init__(
        self,
        name: str,
        func: Callable[[RecordingContext], Dict[str, float]],
        columns: Optional[Sequence[str]] = None,
        description: str = "",
    ) -> None:
        self.name = name
        self.func = func
        self.columns = tuple(columns or ())
        self.description = description or (func.__doc__ or "").strip().split("\n")[0]

    def compute(self, ctx):
        return dict(self.func(ctx))


# ------------------------------------------------------------------ #
# Registry                                                             #
# ------------------------------------------------------------------ #

AVAILABLE_FEATURE_GROUPS: Dict[str, FeatureGroup] = {
    g.name: g for g in (RhythmFeatures(), IntervalFeatures(), HRVFeatures(), AmplitudeFeatures())
}

FeatureSpec = Union[str, FeatureGroup, Callable[[RecordingContext], Dict[str, float]]]


def register_feature_group(group: FeatureGroup, overwrite: bool = False) -> FeatureGroup:
    """Register a :class:`FeatureGroup` instance so it can be selected by name."""
    if not group.name:
        raise ValueError("Feature group needs a name.")
    if group.name in AVAILABLE_FEATURE_GROUPS and not overwrite:
        raise ValueError(f"Feature group {group.name!r} already registered "
                         "(pass overwrite=True).")
    clash = set(group.columns) & {c for g in AVAILABLE_FEATURE_GROUPS.values()
                                  if g.name != group.name for c in g.columns}
    if clash:
        raise ValueError(f"Columns {sorted(clash)} already belong to another feature group.")
    AVAILABLE_FEATURE_GROUPS[group.name] = group
    return group


def feature_group(
    name: str, columns: Optional[Sequence[str]] = None, description: str = "",
    overwrite: bool = False,
):
    """Decorator registering ``func(ctx) -> dict`` as a feature group."""
    def deco(func):
        register_feature_group(FunctionFeatureGroup(name, func, columns, description),
                               overwrite=overwrite)
        return func
    return deco


def available_features() -> Dict[str, Tuple[str, ...]]:
    """Mapping of registered group name → its column names."""
    return {name: g.columns for name, g in AVAILABLE_FEATURE_GROUPS.items()}


def resolve_features(
    features: Union[None, FeatureSpec, Iterable[FeatureSpec]],
) -> List[Tuple[FeatureGroup, Optional[List[str]]]]:
    """
    Turn a feature selection into the groups to run.

    ``features`` may be ``None`` / ``"all"`` (every registered group), or any mix of group
    names, column names, :class:`FeatureGroup` instances and ``func(ctx) -> dict`` callables.

    Returns
    -------
    list of ``(group, columns)`` — ``columns`` lists the columns of that group to keep, or is
    None to keep all of them.
    """
    if features is None or (isinstance(features, str) and features == "all"):
        return [(g, None) for g in AVAILABLE_FEATURE_GROUPS.values()]
    if isinstance(features, (str, FeatureGroup)) or callable(features):
        features = [features]

    column_owner = {c: g for g in AVAILABLE_FEATURE_GROUPS.values() for c in g.columns}
    selected: Dict[str, Tuple[FeatureGroup, Optional[List[str]]]] = {}

    def add(group: FeatureGroup, column: Optional[str] = None) -> None:
        if column is None:
            selected[group.name] = (group, None)
            return
        _, cols = selected.setdefault(group.name, (group, []))
        if cols is not None and column not in cols:
            cols.append(column)

    for spec in features:
        if isinstance(spec, FeatureGroup):
            add(spec)
        elif isinstance(spec, str) and spec == "all":
            for g in AVAILABLE_FEATURE_GROUPS.values():
                add(g)
        elif isinstance(spec, str) and spec in AVAILABLE_FEATURE_GROUPS:
            add(AVAILABLE_FEATURE_GROUPS[spec])
        elif isinstance(spec, str) and spec in column_owner:
            add(column_owner[spec], spec)
        elif callable(spec):
            add(FunctionFeatureGroup(spec.__name__, spec))
        else:
            raise ValueError(
                f"Unknown feature {spec!r}. Groups: {sorted(AVAILABLE_FEATURE_GROUPS)}; "
                f"columns: {sorted(column_owner)}"
            )
    return list(selected.values())
