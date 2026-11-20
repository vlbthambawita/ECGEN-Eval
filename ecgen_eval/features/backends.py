"""
Delineation backends: the library that finds the beats and their fiducial points.

A backend turns one recording into R peaks and a dict of fiducial arrays aligned with them
(element ``i`` belongs to beat ``i``, NaN when missing). Feature groups
(:mod:`ecgen_eval.features.groups`) only read these, so any backend works with any feature.

Fiducial keys understood by the built-in feature groups:

``ECG_QRS_Onsets``, ``ECG_QRS_Offsets``, ``ECG_P_Onsets``, ``ECG_P_Offsets``,
``ECG_T_Peaks``, ``ECG_T_Offsets``.

Built-in backends
-----------------
- ``hybrid`` (default): NeuroKit2 R peaks, multi-lead spatial-velocity QRS boundaries,
  NeuroKit2 prominence P/T on every lead with tangent-method T offset (validated against
  GE 12SL, see :mod:`ecgen_eval.features.delineation`).
- ``neurokit2``: plain NeuroKit2 ``ecg_peaks`` + ``ecg_delineate`` (``dwt``, ``cwt``,
  ``peak`` or ``prominence``) on the primary lead, or every lead combined with the median.
- ``scipy``: no NeuroKit2. SciPy Pan-Tompkins R peaks + spatial-velocity QRS boundaries; P
  and T fiducials are absent, so PR, QT, QTc and P duration are NaN.
- ``biosppy``: BioSPPy R-peak segmenters (Hamilton, Christov, ...) and template-based
  ``getP/Q/S/TPositions`` on the primary lead, or every lead combined with the median.
- ``heartpy``: HeartPy R peaks only (PPG-oriented moving-average detector); intervals and
  amplitudes are NaN.

Add your own with :func:`register_backend`.
"""

from __future__ import annotations

import importlib.util
import inspect
from typing import Dict, Optional, Tuple, Type, Union

import numpy as np

from ecgen_eval.features.delineation import align_to_beats, delineate_recording
from ecgen_eval.features.qrs_detection import detect_rpeaks


#: Fiducial keys understood by the built-in feature groups.
FIDUCIAL_KEYS = (
    "ECG_QRS_Onsets", "ECG_QRS_Offsets", "ECG_P_Onsets", "ECG_P_Offsets",
    "ECG_T_Peaks", "ECG_T_Offsets",
)


def _median_across_leads(per_lead: Dict[str, list], n_beats: int) -> Dict[str, np.ndarray]:
    """Per-beat median over leads of beat-aligned fiducial arrays (NaN where no lead has one)."""
    waves = {}
    for k, arrays in per_lead.items():
        if not arrays:
            waves[k] = np.full(n_beats, np.nan)
            continue
        stack = np.stack(arrays)
        with np.errstate(all="ignore"):
            waves[k] = np.array([np.nanmedian(c) if np.isfinite(c).any() else np.nan
                                 for c in stack.T])
    return waves


class DelineationBackend:
    """
    Base class for delineation backends.

    Subclasses set ``name`` (and optionally ``description`` / ``requires``) and implement
    :meth:`delineate`. Constructors must be callable with keyword arguments only.

    ``rpeak_methods`` and ``delineation_methods`` list the values accepted for the
    constructor's ``rpeak_method`` and ``method`` arguments; :func:`get_backend` checks them
    when non-empty (an empty tuple means the backend does not restrict the value).
    """

    name: str = ""
    description: str = ""
    requires: Tuple[str, ...] = ()
    rpeak_methods: Tuple[str, ...] = ()
    delineation_methods: Tuple[str, ...] = ()

    @classmethod
    def is_available(cls) -> bool:
        """True when every package in ``requires`` can be imported."""
        return all(importlib.util.find_spec(pkg) is not None for pkg in cls.requires)

    def delineate(
        self, recording: np.ndarray, fs: float, primary_lead_idx: int
    ) -> Tuple[np.ndarray, Optional[Dict[str, np.ndarray]]]:
        """
        Parameters
        ----------
        recording : (L, T) ECG.
        fs : float
        primary_lead_idx : int — lead whose R peaks define the beats.

        Returns
        -------
        (rpeaks, waves) — sorted R-peak sample indices, and fiducial arrays aligned with them
        (``None`` when the recording could not be delineated).
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"


class HybridBackend(DelineationBackend):
    """
    Default backend: NeuroKit2 R peaks, spatial-velocity QRS, NeuroKit2 P/T on every lead.

    Parameters
    ----------
    rpeak_method : str
        ``nk.ecg_peaks`` method, or ``"scipy"`` for the SciPy Pan-Tompkins detector.
    method : str
        ``nk.ecg_delineate`` method for the P and T waves (default ``"prominence"``).
    pt_waves : bool
        Delineate P and T waves (needs NeuroKit2).
    """

    name = "hybrid"
    description = (
        "NeuroKit2 R peaks + multi-lead spatial-velocity QRS + NeuroKit2 prominence P/T "
        "with tangent T offset (default, validated against GE 12SL)"
    )
    requires = ("neurokit2", "scipy")
    delineation_methods = ("prominence", "dwt", "cwt", "peak")

    def __init__(
        self, rpeak_method: str = "neurokit", method: str = "prominence", pt_waves: bool = True
    ) -> None:
        self.rpeak_method = rpeak_method
        self.method = method
        self.pt_waves = pt_waves

    def delineate(self, recording, fs, primary_lead_idx):
        primary = recording[primary_lead_idx].astype(float)
        rpeaks = detect_rpeaks(primary, fs, method=self.rpeak_method)
        waves = delineate_recording(
            recording, rpeaks, fs, method=self.method, pt_waves=self.pt_waves
        )
        return rpeaks, waves

    def __repr__(self) -> str:
        return (f"HybridBackend(rpeak_method={self.rpeak_method!r}, method={self.method!r}, "
                f"pt_waves={self.pt_waves})")


class ScipyBackend(HybridBackend):
    """SciPy-only backend: Pan-Tompkins R peaks and spatial-velocity QRS, no P/T waves."""

    name = "scipy"
    description = (
        "SciPy Pan-Tompkins R peaks + spatial-velocity QRS; no P/T waves "
        "(PR, QT, QTc, P duration are NaN)"
    )
    requires = ("scipy",)
    delineation_methods = ()

    def __init__(self, rpeak_method: str = "scipy") -> None:
        super().__init__(rpeak_method=rpeak_method, pt_waves=False)

    def __repr__(self) -> str:
        return f"ScipyBackend(rpeak_method={self.rpeak_method!r})"


#: NeuroKit2 output key → key used by the feature groups.
_NK_KEY_MAP = {
    "ECG_R_Onsets": "ECG_QRS_Onsets",
    "ECG_R_Offsets": "ECG_QRS_Offsets",
    "ECG_P_Onsets": "ECG_P_Onsets",
    "ECG_P_Offsets": "ECG_P_Offsets",
    "ECG_T_Peaks": "ECG_T_Peaks",
    "ECG_T_Offsets": "ECG_T_Offsets",
}


class NeuroKitBackend(DelineationBackend):
    """
    Plain NeuroKit2 pipeline: ``nk.ecg_clean`` → ``nk.ecg_peaks`` → ``nk.ecg_delineate``.

    Parameters
    ----------
    method : str
        ``nk.ecg_delineate`` method: ``"dwt"`` (default), ``"cwt"``, ``"peak"`` or
        ``"prominence"``. ``"peak"`` gives no QRS boundaries, so QRS duration and the QRS
        onset-based intervals (PR, QT) are NaN.
    rpeak_method : str
        ``nk.ecg_peaks`` method.
    leads : str
        ``"primary"`` delineates the primary lead only; ``"all"`` delineates every lead at
        the primary lead's R peaks and takes the median across leads.
    """

    name = "neurokit2"
    description = "Plain NeuroKit2 ecg_peaks + ecg_delineate (dwt / cwt / peak / prominence)"
    requires = ("neurokit2",)
    delineation_methods = ("dwt", "cwt", "peak", "prominence")

    def __init__(
        self, method: str = "dwt", rpeak_method: str = "neurokit", leads: str = "primary"
    ) -> None:
        if leads not in ("primary", "all"):
            raise ValueError(f"leads must be 'primary' or 'all', got {leads!r}")
        self.method = method
        self.rpeak_method = rpeak_method
        self.leads = leads

    def delineate(self, recording, fs, primary_lead_idx):
        import neurokit2 as nk

        sr = int(fs)
        clean = nk.ecg_clean(recording[primary_lead_idx].astype(float), sampling_rate=sr)
        _, info = nk.ecg_peaks(clean, sampling_rate=sr, method=self.rpeak_method)
        rpeaks = np.asarray(info["ECG_R_Peaks"], dtype=int)
        rpeaks = rpeaks[rpeaks >= 0]
        if len(rpeaks) < 2:
            return rpeaks, None

        lead_idx = [primary_lead_idx] if self.leads == "primary" else range(len(recording))
        per_lead = {k: [] for k in _NK_KEY_MAP.values()}
        for i in lead_idx:
            try:
                sig = nk.ecg_clean(recording[i].astype(float), sampling_rate=sr)
                _, w = nk.ecg_delineate(sig, rpeaks, sampling_rate=sr, method=self.method)
            except Exception:  # flat / too short / delineation failure on this lead
                continue
            for src, dst in _NK_KEY_MAP.items():
                per_lead[dst].append(align_to_beats(w.get(src), rpeaks))

        return rpeaks, _median_across_leads(per_lead, len(rpeaks))

    def __repr__(self) -> str:
        return (f"NeuroKitBackend(method={self.method!r}, rpeak_method={self.rpeak_method!r}, "
                f"leads={self.leads!r})")


#: ``rpeak_method`` → BioSPPy segmenter in ``biosppy.signals.ecg``.
_BIOSPPY_SEGMENTERS = {
    "hamilton": "hamilton_segmenter",
    "christov": "christov_segmenter",
    "engzee": "engzee_segmenter",
    "gamboa": "gamboa_segmenter",
    "ssf": "ssf_segmenter",
    "asi": "ASI_segmenter",
    "pantompkins": "Pan_Tompkins_Plus_Plus_segmenter",
}

#: BioSPPy wave-position function → {its output field: key used by the feature groups}.
_BIOSPPY_FIELDS = {
    "getQPositions": {"Q_start_positions": "ECG_QRS_Onsets"},
    "getSPositions": {"S_end_positions": "ECG_QRS_Offsets"},
    "getPPositions": {"P_start_positions": "ECG_P_Onsets", "P_end_positions": "ECG_P_Offsets"},
    "getTPositions": {"T_positions": "ECG_T_Peaks", "T_end_positions": "ECG_T_Offsets"},
}

#: Heartbeat template window around each R peak (s), as in ``biosppy.signals.ecg.ecg``.
_BIOSPPY_BEFORE, _BIOSPPY_AFTER = 0.2, 0.4


class BioSPPyBackend(DelineationBackend):
    """
    BioSPPy: R-peak segmenters + template-based P/Q/S/T positions.

    The primary lead is band-passed as in ``biosppy.signals.ecg.ecg`` (FIR, 0.67-45 Hz), R
    peaks come from a BioSPPy segmenter refined with ``correct_rpeaks``, and the fiducials from
    ``getQPositions`` (QRS onset = Q start), ``getSPositions`` (QRS offset = S end),
    ``getPPositions`` and ``getTPositions`` on heartbeat templates (-0.2 s to +0.4 s). These
    are rule-based local extrema of each template: an absent Q or S wave, an inverted T wave
    or a T wave ending after +0.4 s give wrong or missing points.

    Parameters
    ----------
    rpeak_method : str
        BioSPPy segmenter: ``"hamilton"`` (default), ``"christov"``, ``"engzee"``,
        ``"gamboa"``, ``"ssf"``, ``"asi"`` or ``"pantompkins"`` (Pan-Tompkins++).
    leads : str
        ``"primary"`` delineates the primary lead only; ``"all"`` delineates every lead at
        the primary lead's R peaks and takes the median across leads.
    filtered : bool
        Band-pass every lead before segmenting and delineating (BioSPPy's own pipeline).
    """

    name = "biosppy"
    description = (
        "BioSPPy R-peak segmenters + template-based P/Q/S/T positions "
        "(getP/Q/S/TPositions)"
    )
    requires = ("biosppy", "peakutils")
    rpeak_methods = tuple(_BIOSPPY_SEGMENTERS)

    def __init__(
        self, rpeak_method: str = "hamilton", leads: str = "primary", filtered: bool = True
    ) -> None:
        if rpeak_method not in _BIOSPPY_SEGMENTERS:
            raise ValueError(f"Unknown BioSPPy R-peak method {rpeak_method!r}. "
                             f"Choose from: {', '.join(_BIOSPPY_SEGMENTERS)}")
        if leads not in ("primary", "all"):
            raise ValueError(f"leads must be 'primary' or 'all', got {leads!r}")
        self.rpeak_method = rpeak_method
        self.leads = leads
        self.filtered = filtered

    def _filter(self, signal: np.ndarray, fs: float) -> np.ndarray:
        signal = signal.astype(float)
        if not self.filtered:
            return signal - np.mean(signal)
        from biosppy.signals import tools

        # BioSPPy uses order 1.5 * fs; shorten it so filtfilt still fits short recordings.
        order = min(int(1.5 * fs), (len(signal) - 1) // 3 - 1)
        filtered, _, _ = tools.filter_signal(signal=signal, ftype="FIR", band="bandpass",
                                             order=order, frequency=[0.67, 45],
                                             sampling_rate=fs)
        return filtered - np.mean(filtered)

    @staticmethod
    def _lead_fiducials(signal: np.ndarray, rpeaks: np.ndarray, fs: float
                        ) -> Dict[str, np.ndarray]:
        """Fiducials of one lead at the given R peaks, aligned with ``rpeaks``."""
        from biosppy.signals import ecg as becg

        templates, kept = becg.extract_heartbeats(signal=signal, rpeaks=rpeaks,
                                                  sampling_rate=fs, before=_BIOSPPY_BEFORE,
                                                  after=_BIOSPPY_AFTER)
        if len(kept) == 0:
            return {}
        ts = np.linspace(-_BIOSPPY_BEFORE, _BIOSPPY_AFTER, templates.shape[1], endpoint=False)
        out = {}
        for func_name, fields in _BIOSPPY_FIELDS.items():
            func = getattr(becg, func_name)
            try:
                res = func({"templates": templates, "templates_ts": ts, "rpeaks": kept})
                values = {src: res[src] for src in fields}
            except Exception:
                # One beat without the expected extremum aborts the whole call in some
                # BioSPPy functions: retry beat by beat.
                values = {src: [] for src in fields}
                for t, r in zip(templates, kept):
                    try:
                        res = func({"templates": t[None], "templates_ts": ts,
                                    "rpeaks": np.array([r])})
                    except Exception:
                        continue
                    for src in fields:
                        values[src].extend(res[src])
            for src, dst in fields.items():
                out[dst] = align_to_beats(values[src], rpeaks)
        return out

    def delineate(self, recording, fs, primary_lead_idx):
        from biosppy.signals import ecg as becg

        fs = float(fs)
        primary = self._filter(recording[primary_lead_idx], fs)
        segmenter = getattr(becg, _BIOSPPY_SEGMENTERS[self.rpeak_method])
        (rpeaks,) = segmenter(signal=primary, sampling_rate=fs)
        if len(rpeaks) == 0:
            return np.array([], dtype=int), None
        (rpeaks,) = becg.correct_rpeaks(signal=primary, rpeaks=rpeaks, sampling_rate=fs,
                                        tol=0.05)
        rpeaks = np.unique(np.asarray(rpeaks, dtype=int))
        if len(rpeaks) < 2:
            return rpeaks, None

        lead_idx = [primary_lead_idx] if self.leads == "primary" else range(len(recording))
        per_lead = {k: [] for k in FIDUCIAL_KEYS}
        for i in lead_idx:
            try:
                sig = primary if i == primary_lead_idx else self._filter(recording[i], fs)
                fiducials = self._lead_fiducials(sig, rpeaks, fs)
            except Exception:  # flat / too short / delineation failure on this lead
                continue
            for k, v in fiducials.items():
                per_lead[k].append(v)
        return rpeaks, _median_across_leads(per_lead, len(rpeaks))

    def __repr__(self) -> str:
        return (f"BioSPPyBackend(rpeak_method={self.rpeak_method!r}, leads={self.leads!r}, "
                f"filtered={self.filtered})")


class HeartPyBackend(DelineationBackend):
    """
    HeartPy: R peaks only (rhythm and HRV features; intervals and amplitudes are NaN).

    HeartPy was designed for PPG. Following its ECG guidance the primary lead is notch-filtered
    at 0.05 Hz (baseline wander), scaled and upsampled before ``hp.process``, whose
    moving-average detector prefers broad peaks. Peaks HeartPy rejects are dropped, and every
    peak is moved to the largest sample within 50 ms at the original rate.

    Parameters
    ----------
    upsample : int
        Upsampling factor before peak detection (HeartPy suggests 2-6 for ECG).
    bpmmin, bpmmax : float
        Heart-rate range used by HeartPy's threshold optimisation.
    windowsize : float
        Moving-average window (s).
    keep_rejected : bool
        Keep the peaks HeartPy marks as rejected (``removed_beats``).
    """

    name = "heartpy"
    description = (
        "HeartPy moving-average R-peak detector; no P/QRS/T delineation "
        "(only rhythm and HRV features)"
    )
    requires = ("heartpy", "scipy")

    def __init__(
        self, upsample: int = 4, bpmmin: float = 40, bpmmax: float = 180,
        windowsize: float = 0.75, keep_rejected: bool = False,
    ) -> None:
        if int(upsample) < 1:
            raise ValueError(f"upsample must be >= 1, got {upsample!r}")
        self.upsample = int(upsample)
        self.bpmmin = bpmmin
        self.bpmmax = bpmmax
        self.windowsize = windowsize
        self.keep_rejected = keep_rejected

    def delineate(self, recording, fs, primary_lead_idx):
        import heartpy as hp
        from scipy.signal import resample

        empty = np.array([], dtype=int)
        signal = recording[primary_lead_idx].astype(float)
        if not np.all(np.isfinite(signal)) or np.ptp(signal) == 0:
            return empty, None
        try:
            clean = hp.filter_signal(signal, cutoff=0.05, sample_rate=fs, filtertype="notch")
            up = resample(hp.scale_data(clean), len(clean) * self.upsample)
            wd, _ = hp.process(up, sample_rate=fs * self.upsample, windowsize=self.windowsize,
                               bpmmin=self.bpmmin, bpmmax=self.bpmmax)
        except Exception:  # hp.exceptions.BadSignalWarning, too few peaks, ...
            return empty, None

        peaks = np.asarray(wd["peaklist"], dtype=int)
        if not self.keep_rejected and len(wd["removed_beats"]):
            peaks = np.setdiff1d(peaks, np.asarray(wd["removed_beats"], dtype=int))
        peaks = np.round(peaks / self.upsample).astype(int)

        half = max(1, int(round(0.05 * fs)))
        snapped = [max(p - half, 0) + int(np.argmax(clean[max(p - half, 0):p + half + 1]))
                   for p in peaks if 0 <= p < len(clean)]
        return np.unique(np.asarray(snapped, dtype=int)), None

    def __repr__(self) -> str:
        return (f"HeartPyBackend(upsample={self.upsample}, bpmmin={self.bpmmin}, "
                f"bpmmax={self.bpmmax}, windowsize={self.windowsize}, "
                f"keep_rejected={self.keep_rejected})")


# ------------------------------------------------------------------ #
# Registry                                                             #
# ------------------------------------------------------------------ #

AVAILABLE_BACKENDS: Dict[str, Type[DelineationBackend]] = {
    HybridBackend.name: HybridBackend,
    NeuroKitBackend.name: NeuroKitBackend,
    ScipyBackend.name: ScipyBackend,
    BioSPPyBackend.name: BioSPPyBackend,
    HeartPyBackend.name: HeartPyBackend,
}

DEFAULT_BACKEND = HybridBackend.name


def register_backend(
    cls: Type[DelineationBackend], name: Optional[str] = None, overwrite: bool = False
) -> Type[DelineationBackend]:
    """
    Register a :class:`DelineationBackend` subclass so it can be selected by name.

    Usable as a decorator::

        @register_backend
        class MyBackend(DelineationBackend):
            name = "mylib"
            def delineate(self, recording, fs, primary_lead_idx): ...
    """
    key = name or cls.name
    if not key:
        raise ValueError("Backend needs a name (set the `name` class attribute).")
    if key in AVAILABLE_BACKENDS and not overwrite:
        raise ValueError(f"Backend {key!r} already registered (pass overwrite=True).")
    AVAILABLE_BACKENDS[key] = cls
    return cls


def get_backend(
    backend: Union[str, DelineationBackend, None] = None, **kwargs
) -> DelineationBackend:
    """Return a backend instance from a registered name (kwargs go to its constructor)."""
    if isinstance(backend, DelineationBackend):
        if kwargs:
            raise ValueError("Backend options can only be given with a backend name.")
        return backend
    name = backend or DEFAULT_BACKEND
    if name not in AVAILABLE_BACKENDS:
        raise ValueError(
            f"Unknown feature backend {name!r}. Available: {sorted(AVAILABLE_BACKENDS)}"
        )
    cls = AVAILABLE_BACKENDS[name]
    _check_backend_options(cls, name, kwargs)
    return cls(**kwargs)


#: Constructor argument → user-facing option name in error messages.
_OPTION_NAMES = {"method": "delineation method", "rpeak_method": "R-peak method"}
_ARTICLES = {"method": "a", "rpeak_method": "an"}


def _check_backend_options(cls: Type[DelineationBackend], name: str, kwargs: dict) -> None:
    """Raise ValueError for options the backend does not take or values it does not accept."""
    params = inspect.signature(cls.__init__).parameters
    takes_any = any(p.kind is p.VAR_KEYWORD for p in params.values())
    for key in kwargs:
        if key not in params and not takes_any:
            raise ValueError(
                f"The {name!r} backend does not take {_ARTICLES.get(key, 'a')} "
                f"{_OPTION_NAMES.get(key, repr(key) + ' option')}."
            )
    for key, allowed in (("method", cls.delineation_methods),
                         ("rpeak_method", cls.rpeak_methods)):
        if key in kwargs and allowed and kwargs[key] not in allowed:
            raise ValueError(
                f"Unknown {_OPTION_NAMES[key]} {kwargs[key]!r} for the {name!r} backend. "
                f"Choose from: {', '.join(allowed)}"
            )
