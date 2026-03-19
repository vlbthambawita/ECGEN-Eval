"""
ECG graph paper background builder.

Creates a Plotly Figure pre-configured with the traditional ECG paper look:
  - Pink/salmon background
  - Light-red minor grid  (1 mm  = 0.04 s  × 0.1 mV at 25 mm/s, 10 mm/mV)
  - Dark-red major grid   (5 mm  = 0.20 s  × 0.5 mV)

All other visualization modules call ``make_ecg_paper_figure()`` as a factory
and add traces on top of the returned figure.

Reference for standard ECG paper dimensions:
  Kligfield, P., et al. (2007). Recommendations for the Standardization and
  Interpretation of the Electrocardiogram. *Journal of the American College
  of Cardiology*, 49(10), 1109–1127.
  https://doi.org/10.1016/j.jacc.2007.01.024
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ------------------------------------------------------------------ #
# ECG paper constants (standard clinical values)                      #
# ------------------------------------------------------------------ #

# Paper speed and gain
PAPER_SPEED_MM_PER_S = 25.0   # mm/s
GAIN_MM_PER_MV = 10.0         # mm/mV

# Grid spacings in physical units
MINOR_GRID_S = 0.04           # seconds  (1 mm)
MAJOR_GRID_S = 0.20           # seconds  (5 mm)
MINOR_GRID_MV = 0.10          # millivolts (1 mm)
MAJOR_GRID_MV = 0.50          # millivolts (5 mm)

# Colours
BG_COLOR = "rgb(255, 236, 230)"           # classic ECG pink
MINOR_GRID_COLOR = "rgba(220, 100, 100, 0.35)"
MAJOR_GRID_COLOR = "rgba(180, 40, 40, 0.80)"
TRACE_REAL_COLOR = "rgb(10, 10, 10)"      # near-black
SYNTH_PALETTE = [
    "rgb(30, 100, 200)",   # blue
    "rgb(200, 100, 30)",   # orange
    "rgb(40, 160, 60)",    # green
    "rgb(160, 40, 160)",   # purple
    "rgb(200, 40, 80)",    # red
]


def make_ecg_paper_figure(
    n_rows: int,
    n_cols: int,
    row_labels: Optional[List[str]] = None,
    col_labels: Optional[List[str]] = None,
    x_range: Optional[Tuple[float, float]] = None,
    y_range: Optional[Tuple[float, float]] = None,
    fs: float = 500.0,
    subplot_height_px: int = 180,
    subplot_width_px: int = 380,
    shared_xaxes: bool = True,
    shared_yaxes: bool = False,
    title: str = "",
) -> go.Figure:
    """
    Build a Plotly Figure with ECG graph-paper styling for a grid of subplots.

    Parameters
    ----------
    n_rows, n_cols : int
        Subplot grid dimensions.
    row_labels, col_labels : list of str, optional
        Axis-level labels added as annotations.
    x_range : (float, float), optional
        X-axis range in seconds. Default derived from minor/major grid defaults.
    y_range : (float, float), optional
        Y-axis range in mV. Default: (-1.5, 1.5).
    fs : float
        Sampling frequency (used only for tick label formatting hints).
    subplot_height_px, subplot_width_px : int
        Pixel size per subplot panel.
    shared_xaxes, shared_yaxes : bool
        Passed to make_subplots.
    title : str
        Figure title.

    Returns
    -------
    go.Figure
        Pre-styled figure; caller adds traces via fig.add_trace(..., row=r, col=c).
    """
    if y_range is None:
        y_range = (-1.6, 1.6)

    fig = make_subplots(
        rows=n_rows,
        cols=n_cols,
        shared_xaxes=shared_xaxes,
        shared_yaxes=shared_yaxes,
        vertical_spacing=0.06,
        horizontal_spacing=0.04,
        subplot_titles=_subplot_titles(row_labels, col_labels, n_rows, n_cols),
    )

    total_h = subplot_height_px * n_rows + 120
    total_w = subplot_width_px * n_cols + 80

    fig.update_layout(
        height=total_h,
        width=total_w,
        paper_bgcolor="white",
        plot_bgcolor=BG_COLOR,
        title_text=title,
        title_font_size=16,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="right",
            x=1,
            font_size=12,
        ),
        margin=dict(l=60, r=30, t=80, b=60),
        hovermode="x unified",
    )

    # Apply ECG paper grid to every subplot axis
    for r in range(1, n_rows + 1):
        for c in range(1, n_cols + 1):
            axis_idx = "" if (r == 1 and c == 1) else str((r - 1) * n_cols + c)
            _style_axis(fig, axis_idx, x_range, y_range)

    return fig


# ------------------------------------------------------------------ #
# Axis styling                                                         #
# ------------------------------------------------------------------ #

def _style_axis(
    fig: go.Figure,
    axis_idx: str,
    x_range: Optional[Tuple[float, float]],
    y_range: Tuple[float, float],
) -> None:
    """Apply ECG paper grid styling to a single subplot's axes."""
    xaxis_key = f"xaxis{axis_idx}"
    yaxis_key = f"yaxis{axis_idx}"

    x_kwargs = dict(
        range=x_range,
        showgrid=True,
        gridcolor=MAJOR_GRID_COLOR,
        gridwidth=1.2,
        dtick=MAJOR_GRID_S,
        minor=dict(
            showgrid=True,
            gridcolor=MINOR_GRID_COLOR,
            gridwidth=0.6,
            dtick=MINOR_GRID_S,
        ),
        zeroline=False,
        tickfont=dict(size=9),
        title_text="Time (s)",
        title_font_size=10,
        linecolor="rgb(150, 150, 150)",
        linewidth=1,
        tickformat=".2f",
        ticks="outside",
        ticklen=4,
    )

    y_kwargs = dict(
        range=y_range,
        showgrid=True,
        gridcolor=MAJOR_GRID_COLOR,
        gridwidth=1.2,
        dtick=MAJOR_GRID_MV,
        minor=dict(
            showgrid=True,
            gridcolor=MINOR_GRID_COLOR,
            gridwidth=0.6,
            dtick=MINOR_GRID_MV,
        ),
        zeroline=True,
        zerolinecolor="rgba(180, 40, 40, 0.5)",
        zerolinewidth=1,
        tickfont=dict(size=9),
        title_text="Amplitude (mV)",
        title_font_size=10,
        linecolor="rgb(150, 150, 150)",
        linewidth=1,
        tickformat=".1f",
        ticks="outside",
        ticklen=4,
    )

    fig.update_layout(
        **{xaxis_key: x_kwargs, yaxis_key: y_kwargs}
    )


# ------------------------------------------------------------------ #
# Helpers                                                              #
# ------------------------------------------------------------------ #

def _subplot_titles(
    row_labels: Optional[List[str]],
    col_labels: Optional[List[str]],
    n_rows: int,
    n_cols: int,
) -> List[str]:
    """
    Build flat list of subplot title strings for make_subplots.
    Row-major order: top-left to bottom-right.
    """
    titles = []
    for r in range(n_rows):
        for c in range(n_cols):
            parts = []
            if col_labels and c < len(col_labels):
                parts.append(col_labels[c])
            if row_labels and r < len(row_labels):
                parts.append(f"({row_labels[r]})")
            titles.append(" ".join(parts) if parts else "")
    return titles


def get_synth_color(index: int) -> str:
    """Return a colour string for the i-th synthetic dataset."""
    return SYNTH_PALETTE[index % len(SYNTH_PALETTE)]
