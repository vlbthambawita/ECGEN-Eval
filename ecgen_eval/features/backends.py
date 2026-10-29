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

Add your own with :func:`register_backend`.
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple, Type, Union

import numpy as np

from ecgen_eval.features.delineation import align_to_beats, delineate_recording
from ecgen_eval.features.qrs_detection import detect_rpeaks


class DelineationBackend:
    """
    Base class for delineation backends.

    Subclasses set ``name`` (and optionally ``description`` / ``requires``) and implement
    :meth:`delineate`. Constructors must be callable with keyword arguments only.
    """

    name: str = ""
    description: str = ""
    requires: Tuple[str, ...] = ()

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

        waves = {}
        for k, arrays in per_lead.items():
            if not arrays:
                waves[k] = np.full(len(rpeaks), np.nan)
                continue
            stack = np.stack(arrays)
            with np.errstate(all="ignore"):
                waves[k] = np.array([np.nanmedian(c) if np.isfinite(c).any() else np.nan
                                     for c in stack.T])
        return rpeaks, waves

    def __repr__(self) -> str:
        return (f"NeuroKitBackend(method={self.method!r}, rpeak_method={self.rpeak_method!r}, "
                f"leads={self.leads!r})")


# ------------------------------------------------------------------ #
# Registry                                                             #
# ------------------------------------------------------------------ #

AVAILABLE_BACKENDS: Dict[str, Type[DelineationBackend]] = {
    HybridBackend.name: HybridBackend,
    NeuroKitBackend.name: NeuroKitBackend,
    ScipyBackend.name: ScipyBackend,
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
    return AVAILABLE_BACKENDS[name](**kwargs)
