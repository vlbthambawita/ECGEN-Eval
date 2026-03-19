"""ECGDataset: in-memory container for a collection of ECG recordings."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import numpy as np


# Standard lead names for 12-lead and 8-lead ECGs
LEADS_12 = ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]
LEADS_8 = ["I", "II", "V1", "V2", "V3", "V4", "V5", "V6"]


@dataclass
class ECGDataset:
    """
    Container for a collection of ECG recordings loaded from a folder.

    Attributes
    ----------
    data : np.ndarray
        Shape (n_samples, n_leads, n_timepoints).
    lead_names : List[str]
        Ordered list of lead names.
    fs : float
        Sampling frequency in Hz.
    source_path : Path
        Folder the data was loaded from.
    label : str
        Human-readable label used in plots/reports (defaults to folder name).
    file_names : List[str]
        Original filenames in load order.
    """

    data: np.ndarray                    # (N, L, T)
    lead_names: List[str]
    fs: float
    source_path: Path
    label: str
    file_names: List[str] = field(default_factory=list)

    # ------------------------------------------------------------------ #
    # Convenience properties                                               #
    # ------------------------------------------------------------------ #

    @property
    def n_samples(self) -> int:
        return self.data.shape[0]

    @property
    def n_leads(self) -> int:
        return self.data.shape[1]

    @property
    def n_timepoints(self) -> int:
        return self.data.shape[2]

    @property
    def duration_sec(self) -> float:
        return self.n_timepoints / self.fs

    @property
    def time_axis(self) -> np.ndarray:
        """Time axis in seconds."""
        return np.arange(self.n_timepoints) / self.fs

    # ------------------------------------------------------------------ #
    # Subsetting helpers                                                   #
    # ------------------------------------------------------------------ #

    def select_leads(self, leads: List[str]) -> "ECGDataset":
        """Return a new ECGDataset restricted to the requested leads."""
        indices = [self.lead_names.index(l) for l in leads]
        return ECGDataset(
            data=self.data[:, indices, :],
            lead_names=leads,
            fs=self.fs,
            source_path=self.source_path,
            label=self.label,
            file_names=self.file_names,
        )

    def sample(self, n: int, seed: Optional[int] = 42) -> "ECGDataset":
        """Return a new ECGDataset with n randomly selected recordings."""
        rng = np.random.default_rng(seed)
        idx = rng.choice(self.n_samples, size=min(n, self.n_samples), replace=False)
        return ECGDataset(
            data=self.data[idx],
            lead_names=self.lead_names,
            fs=self.fs,
            source_path=self.source_path,
            label=self.label,
            file_names=[self.file_names[i] for i in idx] if self.file_names else [],
        )

    def __repr__(self) -> str:
        return (
            f"ECGDataset(label={self.label!r}, n_samples={self.n_samples}, "
            f"leads={self.n_leads}, timepoints={self.n_timepoints}, fs={self.fs} Hz)"
        )
