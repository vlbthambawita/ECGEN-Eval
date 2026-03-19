"""
Multi-format ECG loader.

Supported formats
-----------------
1. NumPy (.npy / .npz) — primary format for ECGEN-FM, ECGEN-VAE, Pulse2Pulse outputs.
2. WFDB records — PTB-XL and other PhysioNet datasets.
3. CSV — legacy and interop format.

All loaders normalise to np.ndarray of shape (N, L, T) and return an ECGDataset.

CSV layouts
-----------
A) Wide format — one file per recording
   Rows = leads, Columns = timepoints
   Shape on disk: (n_leads, n_timepoints)
   Optional header row with lead names; optional index column.

B) Flat format — one file per recording
   Single row of n_leads × n_timepoints values (row-major).
   Column names may be like "I_0", "I_1", ..., "V6_4999".

C) Multi-recording flat — one file for the whole dataset
   Each row is one recording (n_leads × n_timepoints values).

The loader auto-detects which layout applies and normalises to
np.ndarray of shape (N, L, T).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from tqdm import tqdm

from ecgen_eval.data.dataset import ECGDataset, LEADS_12, LEADS_8


# ------------------------------------------------------------------ #
# Public API                                                          #
# ------------------------------------------------------------------ #

def load_ecg_npy(
    path: Union[str, Path],
    fs: float = 500.0,
    label: Optional[str] = None,
    lead_names: Optional[List[str]] = None,
    max_samples: Optional[int] = None,
) -> ECGDataset:
    """
    Load a NumPy array of ECGs saved with ``np.save`` / ``np.savez``.

    The array must have shape ``(N, L, T)`` — samples × leads × timepoints.
    This is the native output format of ECGEN-FM, ECGEN-VAE, and Pulse2Pulse.

    Parameters
    ----------
    path : str or Path
        Path to a ``.npy`` file (single array) or ``.npz`` file (archive).
        For ``.npz`` the first array found is used unless *label* matches a key.
    fs : float
        Sampling frequency in Hz. Default: 500.
    label : str, optional
        Display label. Defaults to stem of the file.
    lead_names : list of str, optional
        Lead name list. Auto-assigned from L if 8 or 12 leads.
    max_samples : int, optional
        Cap number of recordings loaded.

    Returns
    -------
    ECGDataset
    """
    path = Path(path)

    if path.suffix.lower() == ".npz":
        archive = np.load(path)
        key = label if label in archive else list(archive.keys())[0]
        arr = archive[key]
    else:
        arr = np.load(path, allow_pickle=False)

    if arr.ndim == 2:
        # Single recording (L, T) → (1, L, T)
        arr = arr[np.newaxis]
    if arr.ndim != 3:
        raise ValueError(f"Expected array of shape (N, L, T), got {arr.shape}")

    if max_samples is not None:
        arr = arr[:max_samples]

    arr = arr.astype(np.float32)
    n_leads = arr.shape[1]

    if lead_names is None:
        lead_names = _default_lead_names(n_leads)
    if label is None:
        label = path.stem

    return ECGDataset(
        data=arr,
        lead_names=lead_names,
        fs=fs,
        source_path=path.parent,
        label=label,
        file_names=[path.name] * arr.shape[0],
    )


def load_ecg_wfdb(
    record_dir: Union[str, Path],
    fs: float = 500.0,
    label: Optional[str] = None,
    lead_names: Optional[List[str]] = None,
    max_samples: Optional[int] = None,
    resample_to: Optional[float] = None,
) -> ECGDataset:
    """
    Load WFDB ECG records from a directory (e.g. PTB-XL).

    Requires the ``wfdb`` package (``pip install wfdb``).

    Parameters
    ----------
    record_dir : str or Path
        Directory containing ``.hea`` / ``.dat`` WFDB record pairs,
        or a single record path (without extension).
    fs : float
        Expected sampling frequency. Used for metadata only unless *resample_to* is set.
    label : str, optional
        Display label. Defaults to directory name.
    lead_names : list of str, optional
        Override lead names (e.g. to match a specific lead ordering).
    max_samples : int, optional
        Cap on number of records loaded.
    resample_to : float, optional
        If provided, resample each record to this sampling rate using scipy.

    Returns
    -------
    ECGDataset
    """
    try:
        import wfdb
    except ImportError as e:
        raise ImportError("wfdb package required: pip install wfdb") from e

    record_dir = Path(record_dir)

    # Support single record path (no extension)
    if not record_dir.is_dir():
        parent = record_dir.parent
        stem = record_dir.stem
        record_paths = [parent / stem]
    else:
        hea_files = sorted(record_dir.glob("*.hea"))
        if not hea_files:
            raise FileNotFoundError(f"No WFDB .hea files found in {record_dir}")
        record_paths = [f.parent / f.stem for f in hea_files]

    if label is None:
        label = record_dir.name if record_dir.is_dir() else record_dir.stem

    if max_samples is not None:
        record_paths = record_paths[:max_samples]

    recordings = []
    detected_lead_names: Optional[List[str]] = lead_names
    actual_fs = fs

    for rpath in tqdm(record_paths, desc=f"Loading {label} (WFDB)", unit="rec"):
        try:
            rec = wfdb.rdrecord(str(rpath))
            sig = rec.p_signal  # (T, L) float64
            if sig is None:
                continue
            sig = sig.T.astype(np.float32)  # (L, T)

            if resample_to is not None and rec.fs != resample_to:
                sig = _resample_leads(sig, rec.fs, resample_to)
                actual_fs = resample_to
            else:
                actual_fs = rec.fs or fs

            if detected_lead_names is None:
                detected_lead_names = rec.sig_name

            recordings.append(sig)
        except Exception:
            continue

    if not recordings:
        raise ValueError(f"No valid WFDB records loaded from {record_dir}")

    data = np.stack(recordings, axis=0)  # (N, L, T)
    n_leads = data.shape[1]
    if detected_lead_names is None:
        detected_lead_names = _default_lead_names(n_leads)

    return ECGDataset(
        data=data,
        lead_names=detected_lead_names,
        fs=float(actual_fs),
        source_path=record_dir if record_dir.is_dir() else record_dir.parent,
        label=label,
        file_names=[p.name for p in record_paths],
    )


def load_ecg_folder(
    folder: Union[str, Path],
    fs: float = 500.0,
    label: Optional[str] = None,
    n_leads: Optional[int] = None,
    n_timepoints: Optional[int] = None,
    lead_names: Optional[List[str]] = None,
    max_samples: Optional[int] = None,
) -> ECGDataset:
    """
    Load ECGs from *folder* or a single file, auto-detecting the format.

    Supported: ``.npy`` / ``.npz`` (NumPy), ``.hea`` / WFDB records, and ``.csv``.

    Parameters
    ----------
    folder : str or Path
        Directory or a single file path.
    fs : float
        Sampling frequency in Hz (default 500 Hz).
    label : str, optional
        Display label for plots. Defaults to the folder/file name.
    n_leads : int, optional
        Expected number of leads (8 or 12). Auto-detected if None. (CSV only)
    n_timepoints : int, optional
        Expected number of timepoints per lead. Auto-detected if None. (CSV only)
    lead_names : list of str, optional
        Explicit lead name list. Auto-detected or default-assigned if None.
    max_samples : int, optional
        Cap the number of loaded recordings (useful for quick tests).

    Returns
    -------
    ECGDataset
    """
    path = Path(folder)

    # ---- NumPy single file -------------------------------------------------
    if path.is_file() and path.suffix.lower() in (".npy", ".npz"):
        return load_ecg_npy(path, fs=fs, label=label, lead_names=lead_names,
                            max_samples=max_samples)

    # ---- NumPy folder (multiple .npy files) --------------------------------
    if path.is_dir():
        npy_files = sorted(path.glob("*.npy"))
        if npy_files:
            return _load_npy_folder(npy_files, fs=fs, label=label or path.name,
                                    lead_names=lead_names, max_samples=max_samples)

        npz_files = sorted(path.glob("*.npz"))
        if npz_files:
            return _load_npy_folder(npz_files, fs=fs, label=label or path.name,
                                    lead_names=lead_names, max_samples=max_samples)

    # ---- WFDB folder -------------------------------------------------------
    if path.is_dir() and any(path.glob("*.hea")):
        return load_ecg_wfdb(path, fs=fs, label=label, lead_names=lead_names,
                             max_samples=max_samples)

    # ---- CSV (legacy / interop) --------------------------------------------
    return _load_ecg_csv(path, fs=fs, label=label, n_leads=n_leads,
                         n_timepoints=n_timepoints, lead_names=lead_names,
                         max_samples=max_samples)


# ------------------------------------------------------------------ #
# NumPy folder loader (multiple .npy files — one per recording)       #
# ------------------------------------------------------------------ #

def _load_npy_folder(
    npy_files: List[Path],
    fs: float,
    label: str,
    lead_names: Optional[List[str]],
    max_samples: Optional[int],
) -> ECGDataset:
    if max_samples is not None:
        npy_files = npy_files[:max_samples]

    recordings = []
    file_names = []
    for f in tqdm(npy_files, desc=f"Loading {label} (.npy)", unit="file"):
        try:
            arr = np.load(f, allow_pickle=False).astype(np.float32)
            if arr.ndim == 3:
                for i in range(arr.shape[0]):
                    recordings.append(arr[i])
                    file_names.append(f.name)
            elif arr.ndim == 2:
                recordings.append(arr)
                file_names.append(f.name)
        except Exception:
            continue

    if not recordings:
        raise ValueError(f"No valid .npy files loaded from the folder")

    data = np.stack(recordings, axis=0)
    n_leads = data.shape[1]
    if lead_names is None:
        lead_names = _default_lead_names(n_leads)

    return ECGDataset(
        data=data,
        lead_names=lead_names,
        fs=fs,
        source_path=npy_files[0].parent,
        label=label,
        file_names=file_names,
    )


# ------------------------------------------------------------------ #
# CSV loader (original implementation, extracted to helper)           #
# ------------------------------------------------------------------ #

def _load_ecg_csv(
    folder: Path,
    fs: float,
    label: Optional[str],
    n_leads: Optional[int],
    n_timepoints: Optional[int],
    lead_names: Optional[List[str]],
    max_samples: Optional[int],
) -> ECGDataset:
    if folder.is_file() and folder.suffix.lower() == ".csv":
        csv_files = [folder]
        folder = folder.parent
    elif folder.is_dir():
        csv_files = sorted(folder.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in {folder}")
    else:
        raise FileNotFoundError(f"Path not found or not a supported format: {folder}")

    if label is None:
        label = folder.name

    layout, detected_leads, detected_tp = _detect_layout(
        csv_files[0], n_leads, n_timepoints
    )

    if n_leads is None:
        n_leads = detected_leads
    if n_timepoints is None:
        n_timepoints = detected_tp

    if lead_names is None:
        lead_names = _default_lead_names(n_leads)

    if layout == "multi":
        recordings, _ = _load_multi(csv_files[0], n_leads, n_timepoints, max_samples)
        file_names = [csv_files[0].name] * len(recordings)
    else:
        if max_samples is not None:
            csv_files = csv_files[:max_samples]
        recordings = []
        file_names = []
        for f in tqdm(csv_files, desc=f"Loading {label}", unit="file"):
            arr = _load_single(f, layout, n_leads, n_timepoints)
            if arr is not None:
                recordings.append(arr)
                file_names.append(f.name)

    if not recordings:
        raise ValueError(f"Could not load any valid ECG recordings from {folder}")

    data = np.stack(recordings, axis=0)

    return ECGDataset(
        data=data,
        lead_names=lead_names,
        fs=fs,
        source_path=folder,
        label=label,
        file_names=file_names,
    )


# ------------------------------------------------------------------ #
# Layout detection (CSV)                                              #
# ------------------------------------------------------------------ #

def _detect_layout(
    path: Path,
    hint_leads: Optional[int],
    hint_tp: Optional[int],
) -> Tuple[str, int, int]:
    """
    Returns (layout, n_leads, n_timepoints).
    layout is one of: 'wide', 'flat', 'multi'
    """
    df_head = pd.read_csv(path, nrows=20)
    n_rows, n_cols = df_head.shape

    col_lead_match = _parse_lead_columns(df_head.columns.tolist())

    if col_lead_match:
        leads = sorted(col_lead_match.keys())
        n_leads = len(leads)
        n_tp = len(col_lead_match[leads[0]])
        full_df = pd.read_csv(path)
        if len(full_df) > 1:
            return "multi", n_leads, n_tp
        return "flat", n_leads, n_tp

    if n_rows <= 12 and n_cols >= 100:
        try:
            df_head.apply(pd.to_numeric)
            full = pd.read_csv(path, header=None)
            return "wide", full.shape[0], full.shape[1]
        except Exception:
            pass

    full_df = pd.read_csv(path, header=None)
    total_cols = full_df.shape[1]
    if hint_leads and hint_tp:
        if total_cols == hint_leads * hint_tp:
            return "multi", hint_leads, hint_tp

    for nl in [12, 8]:
        if total_cols % nl == 0:
            nt = total_cols // nl
            if 500 <= nt <= 10000:
                return "multi", nl, nt

    return "wide", full_df.shape[0], full_df.shape[1]


def _parse_lead_columns(cols: List[str]):
    pattern = re.compile(r"^([A-Za-z]+[0-9a-zA-Z]*)_(\d+)$")
    lead_cols: dict = {}
    for c in cols:
        m = pattern.match(str(c))
        if m:
            lead = m.group(1)
            idx = int(m.group(2))
            lead_cols.setdefault(lead, []).append((idx, c))
    if not lead_cols:
        return None
    for lead in lead_cols:
        lead_cols[lead] = [c for _, c in sorted(lead_cols[lead])]
    return lead_cols


# ------------------------------------------------------------------ #
# Single-file CSV loaders                                             #
# ------------------------------------------------------------------ #

def _load_single(
    path: Path,
    layout: str,
    n_leads: int,
    n_timepoints: int,
) -> Optional[np.ndarray]:
    """Load one CSV file → np.ndarray shape (n_leads, n_timepoints)."""
    try:
        if layout == "wide":
            df = pd.read_csv(path, header=None)
            arr = df.values.astype(np.float32)
            if arr.shape[1] == n_timepoints + 1:
                arr = arr[:, 1:]
            if arr.shape != (n_leads, n_timepoints):
                arr = _reshape_or_fail(arr, n_leads, n_timepoints)
            return arr

        elif layout == "flat":
            df = pd.read_csv(path)
            col_lead_match = _parse_lead_columns(df.columns.tolist())
            if col_lead_match:
                leads_sorted = _sort_leads(list(col_lead_match.keys()))
                arr = np.stack(
                    [df[col_lead_match[l]].values[0].astype(np.float32) for l in leads_sorted],
                    axis=0,
                )
            else:
                arr = df.values.astype(np.float32).reshape(n_leads, n_timepoints)
            return arr

    except Exception:
        return None


def _load_multi(
    path: Path,
    n_leads: int,
    n_timepoints: int,
    max_samples: Optional[int],
) -> Tuple[List[np.ndarray], List[str]]:
    df = pd.read_csv(path, header=None)
    if max_samples is not None:
        df = df.iloc[:max_samples]
    recordings = []
    for _, row in df.iterrows():
        arr = row.values.astype(np.float32).reshape(n_leads, n_timepoints)
        recordings.append(arr)
    return recordings, []


def _reshape_or_fail(arr: np.ndarray, n_leads: int, n_tp: int) -> np.ndarray:
    total = n_leads * n_tp
    if arr.size == total:
        return arr.flatten()[:total].reshape(n_leads, n_tp)
    raise ValueError(f"Cannot reshape array of size {arr.size} to ({n_leads}, {n_tp})")


# ------------------------------------------------------------------ #
# Resampling helper (WFDB)                                            #
# ------------------------------------------------------------------ #

def _resample_leads(sig: np.ndarray, from_fs: float, to_fs: float) -> np.ndarray:
    """Resample (L, T) array from from_fs to to_fs using scipy."""
    try:
        from scipy.signal import resample_poly
        from math import gcd
        ratio_num = int(to_fs)
        ratio_den = int(from_fs)
        g = gcd(ratio_num, ratio_den)
        up, down = ratio_num // g, ratio_den // g
        return resample_poly(sig, up, down, axis=-1).astype(np.float32)
    except ImportError:
        # Fallback: linear interpolation
        n_out = int(sig.shape[-1] * to_fs / from_fs)
        out = np.zeros((sig.shape[0], n_out), dtype=np.float32)
        x_old = np.linspace(0, 1, sig.shape[-1])
        x_new = np.linspace(0, 1, n_out)
        for i in range(sig.shape[0]):
            out[i] = np.interp(x_new, x_old, sig[i])
        return out


# ------------------------------------------------------------------ #
# Lead name helpers                                                   #
# ------------------------------------------------------------------ #

_LEAD_ORDER = {l: i for i, l in enumerate(LEADS_12)}


def _sort_leads(leads: List[str]) -> List[str]:
    return sorted(leads, key=lambda l: _LEAD_ORDER.get(l, 999))


def _default_lead_names(n_leads: int) -> List[str]:
    if n_leads == 12:
        return LEADS_12
    if n_leads == 8:
        return LEADS_8
    return [f"L{i+1}" for i in range(n_leads)]
