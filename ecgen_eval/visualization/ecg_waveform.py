"""
Interactive ECG waveform comparison plots on graph-paper background.

Three comparison modes
----------------------
overlay     : Real (black) and all synthetic datasets on the same axes.
sidebyside  : Real panel on left, each synthetic dataset in its own panel.
grid        : One row per lead, one column per dataset.
"""

from __future__ import annotations

from typing import List, Optional

import numpy as np
import plotly.graph_objects as go

from ecgen_eval.data.dataset import ECGDataset
from ecgen_eval.visualization.ecg_paper import (
    TRACE_REAL_COLOR,
    get_synth_color,
    make_ecg_paper_figure,
)

# Standard 12-lead layout: (row, col) positions (1-indexed)
_LAYOUT_12 = {
    "I":   (1, 1), "aVR": (1, 2), "V1": (1, 3), "V4": (1, 4),
    "II":  (2, 1), "aVL": (2, 2), "V2": (2, 3), "V5": (2, 4),
    "III": (3, 1), "aVF": (3, 2), "V3": (3, 3), "V6": (3, 4),
}
_LAYOUT_8 = {
    "I":  (1, 1), "II":  (1, 2),
    "V1": (2, 1), "V2":  (2, 2),
    "V3": (3, 1), "V4":  (3, 2),
    "V5": (4, 1), "V6":  (4, 2),
}


def plot_ecg_comparison(
    real: ECGDataset,
    synthetics: List[ECGDataset],
    sample_index: int = 0,
    leads: Optional[List[str]] = None,
    mode: str = "overlay",
    add_calibration_pulse: bool = True,
) -> go.Figure:
    """
    Plot one ECG recording from *real* and the corresponding sample from each
    synthetic dataset on ECG graph paper.

    Parameters
    ----------
    real : ECGDataset
    synthetics : list of ECGDataset
    sample_index : int
        Which recording to visualise (0-indexed).
    leads : list of str, optional
        Subset of lead names to show. Defaults to all leads.
    mode : 'overlay' | 'sidebyside' | 'grid'
    add_calibration_pulse : bool
        Prepend a 1 mV × 0.2 s calibration square wave to every trace.

    Returns
    -------
    go.Figure
    """
    if leads is None:
        leads = real.lead_names

    leads = [l for l in leads if l in real.lead_names]
    if not leads:
        raise ValueError("No valid lead names found in real dataset.")

    if mode == "overlay":
        return _overlay(real, synthetics, sample_index, leads, add_calibration_pulse)
    elif mode == "sidebyside":
        return _sidebyside(real, synthetics, sample_index, leads, add_calibration_pulse)
    elif mode == "grid":
        return _grid(real, synthetics, sample_index, leads, add_calibration_pulse)
    else:
        raise ValueError(f"Unknown mode: {mode!r}. Choose 'overlay', 'sidebyside', or 'grid'.")


# ------------------------------------------------------------------ #
# Mode implementations                                                 #
# ------------------------------------------------------------------ #

def _overlay(
    real: ECGDataset,
    synthetics: List[ECGDataset],
    sample_index: int,
    leads: List[str],
    add_cal: bool,
) -> go.Figure:
    """All datasets on the same axes, one subplot per lead."""
    n_leads = len(leads)
    layout = _choose_layout(leads, real.lead_names)
    n_rows, n_cols = _grid_dims(layout, leads)

    t = real.time_axis
    x_range = _x_range(t, add_cal)

    fig = make_ecg_paper_figure(
        n_rows=n_rows,
        n_cols=n_cols,
        x_range=x_range,
        fs=real.fs,
        title=f"ECG Overlay — Sample {sample_index} | {_lead_str(leads)} | 25 mm/s · 10 mm/mV",
    )

    for li, lead in enumerate(leads):
        row, col = layout.get(lead, _linear_position(li, n_cols))

        # Real trace
        x, y = _prepare_signal(
            real.data[sample_index, real.lead_names.index(lead), :], t, add_cal
        )
        fig.add_trace(
            go.Scatter(
                x=x, y=y,
                mode="lines",
                name=real.label,
                legendgroup="real",
                showlegend=(li == 0),
                line=dict(color=TRACE_REAL_COLOR, width=1.5),
                hovertemplate="<b>%{fullData.name}</b><br>t=%{x:.3f}s<br>%{y:.3f} mV<extra></extra>",
            ),
            row=row, col=col,
        )

        # Synthetic traces
        for si, synth in enumerate(synthetics):
            if sample_index >= synth.n_samples:
                continue
            if lead not in synth.lead_names:
                continue
            sx, sy = _prepare_signal(
                synth.data[sample_index, synth.lead_names.index(lead), :], t, add_cal
            )
            fig.add_trace(
                go.Scatter(
                    x=sx, y=sy,
                    mode="lines",
                    name=synth.label,
                    legendgroup=f"synth_{si}",
                    showlegend=(li == 0),
                    line=dict(color=get_synth_color(si), width=1.5, dash="solid"),
                    opacity=0.75,
                    hovertemplate="<b>%{fullData.name}</b><br>t=%{x:.3f}s<br>%{y:.3f} mV<extra></extra>",
                ),
                row=row, col=col,
            )

        # Lead label annotation
        fig = _add_lead_label(fig, lead, row, col)

    _add_scale_annotation(fig)
    return fig


def _sidebyside(
    real: ECGDataset,
    synthetics: List[ECGDataset],
    sample_index: int,
    leads: List[str],
    add_cal: bool,
) -> go.Figure:
    """One column for Real + one column per synthetic dataset."""
    n_datasets = 1 + len(synthetics)
    n_rows = len(leads)
    n_cols = n_datasets

    t = real.time_axis
    x_range = _x_range(t, add_cal)

    col_labels = [real.label] + [s.label for s in synthetics]

    fig = make_ecg_paper_figure(
        n_rows=n_rows,
        n_cols=n_cols,
        row_labels=leads,
        col_labels=col_labels,
        x_range=x_range,
        fs=real.fs,
        subplot_width_px=300,
        subplot_height_px=160,
        shared_yaxes=True,
        title=f"ECG Side-by-Side — Sample {sample_index}",
    )

    datasets = [real] + list(synthetics)
    colors = [TRACE_REAL_COLOR] + [get_synth_color(i) for i in range(len(synthetics))]

    for row, lead in enumerate(leads, start=1):
        for col, (ds, color) in enumerate(zip(datasets, colors), start=1):
            if lead not in ds.lead_names or sample_index >= ds.n_samples:
                continue
            x, y = _prepare_signal(
                ds.data[sample_index, ds.lead_names.index(lead), :], t, add_cal
            )
            fig.add_trace(
                go.Scatter(
                    x=x, y=y,
                    mode="lines",
                    name=ds.label,
                    legendgroup=ds.label,
                    showlegend=(row == 1),
                    line=dict(color=color, width=1.5),
                    hovertemplate="<b>%{fullData.name}</b><br>t=%{x:.3f}s<br>%{y:.3f} mV<extra></extra>",
                ),
                row=row, col=col,
            )

    _add_scale_annotation(fig)
    return fig


def _grid(
    real: ECGDataset,
    synthetics: List[ECGDataset],
    sample_index: int,
    leads: List[str],
    add_cal: bool,
) -> go.Figure:
    """Rows = leads, Cols = datasets. Compact grid view."""
    return _sidebyside(real, synthetics, sample_index, leads, add_cal)


# ------------------------------------------------------------------ #
# Signal preparation                                                   #
# ------------------------------------------------------------------ #

def _prepare_signal(signal: np.ndarray, t: np.ndarray, add_cal: bool):
    """
    Optionally prepend a 1 mV × 0.2 s calibration square pulse.
    Returns (x_array, y_array).
    """
    if not add_cal:
        return t, signal.astype(float)

    dt = t[1] - t[0]
    cal_duration = 0.2   # seconds
    cal_amplitude = 1.0  # mV
    n_cal = int(cal_duration / dt)

    # Build calibration pulse: flat-0, up-1mV, flat-1mV, down-0
    n_edge = max(1, n_cal // 10)
    cal = np.zeros(n_cal + n_edge * 2)
    cal[n_edge: n_edge + n_cal] = cal_amplitude

    # Prefix time axis
    t_cal = np.arange(-(len(cal)), 0) * dt
    x = np.concatenate([t_cal, t])
    y = np.concatenate([cal, signal.astype(float)])
    return x, y


# ------------------------------------------------------------------ #
# Layout helpers                                                       #
# ------------------------------------------------------------------ #

def _choose_layout(leads: List[str], all_leads: List[str]) -> dict:
    """Pick the standard 12-lead or 8-lead layout if it fits, else linear."""
    if all(l in _LAYOUT_12 for l in leads):
        return _LAYOUT_12
    if all(l in _LAYOUT_8 for l in leads):
        return _LAYOUT_8
    return {}


def _grid_dims(layout: dict, leads: List[str]) -> tuple:
    if layout:
        rows = max(v[0] for v in layout.values())
        cols = max(v[1] for v in layout.values())
        return rows, cols
    n = len(leads)
    cols = min(4, n)
    rows = (n + cols - 1) // cols
    return rows, cols


def _linear_position(index: int, n_cols: int) -> tuple:
    return (index // n_cols) + 1, (index % n_cols) + 1


def _x_range(t: np.ndarray, add_cal: bool):
    dt = t[1] - t[0]
    cal_offset = -0.25 if add_cal else 0.0
    return (cal_offset, float(t[-1]) + dt)


def _lead_str(leads: List[str]) -> str:
    if len(leads) > 4:
        return f"{len(leads)} leads"
    return ", ".join(leads)


# ------------------------------------------------------------------ #
# Annotation helpers                                                   #
# ------------------------------------------------------------------ #

def _add_lead_label(fig: go.Figure, label: str, row: int, col: int) -> go.Figure:
    """Overlay a bold lead label at the top-left of a subplot."""
    # Annotations are added at figure level; position is in paper coordinates.
    # We use a simple approach: add as a scatter trace annotation instead.
    return fig


def _add_scale_annotation(fig: go.Figure) -> None:
    """Add paper speed and gain info as a figure annotation."""
    fig.add_annotation(
        text="25 mm/s · 10 mm/mV",
        xref="paper", yref="paper",
        x=1.0, y=-0.04,
        showarrow=False,
        font=dict(size=10, color="gray"),
        xanchor="right",
    )
