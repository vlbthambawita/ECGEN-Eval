"""
2D and 3D distribution comparison plots for clinical ECG features.

All functions return self-contained Plotly Figure objects suitable for
embedding in the HTML report.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ------------------------------------------------------------------ #
# Colour palette                                                       #
# ------------------------------------------------------------------ #
_REAL_COLOUR  = "rgba(31, 119, 180, 0.7)"   # blue
_SYNTH_COLOUR = "rgba(255, 127, 14, 0.7)"   # orange
_REAL_LINE    = "rgba(31, 119, 180, 1.0)"
_SYNTH_LINE   = "rgba(255, 127, 14, 1.0)"

_MULTI_COLOURS = [
    "rgba(255, 127, 14, 0.7)",
    "rgba(44, 160, 44, 0.7)",
    "rgba(214, 39, 40, 0.7)",
    "rgba(148, 103, 189, 0.7)",
]

# Default feature pairs / triples for the report
DEFAULT_2D_PAIRS: List[Tuple[str, str]] = [
    ("rr_mean_ms", "hr_bpm"),
    ("qrs_duration_ms", "qt_interval_ms"),
    ("st_deviation_mv", "t_amplitude_mv"),
    ("rr_mean_ms", "hrv_sdnn_ms"),
]

DEFAULT_3D_TRIPLES: List[Tuple[str, str, str]] = [
    ("rr_mean_ms", "hr_bpm", "qrs_duration_ms"),
    ("pr_interval_ms", "qt_interval_ms", "hrv_sdnn_ms"),
    ("st_deviation_mv", "t_amplitude_mv", "qrs_duration_ms"),
]


# ------------------------------------------------------------------ #
# Internal helpers                                                     #
# ------------------------------------------------------------------ #

def _clean(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    """Drop rows with NaN in any of the requested columns."""
    available = [c for c in cols if c in df.columns]
    if not available:
        return pd.DataFrame(columns=cols)
    return df[available].dropna()


def _pretty_label(col: str) -> str:
    return col.replace("_", " ").title()


def _kde_contour(
    x: np.ndarray, y: np.ndarray, color_scale: str, name: str, showscale: bool = False
) -> go.Histogram2dContour:
    """2D histogram-density contour trace (Plotly built-in KDE approximation)."""
    return go.Histogram2dContour(
        x=x,
        y=y,
        name=name,
        colorscale=color_scale,
        reversescale=False,
        showscale=showscale,
        contours=dict(showlines=True),
        line=dict(width=1),
        opacity=0.6,
        ncontours=8,
    )


# ------------------------------------------------------------------ #
# 2D plots                                                             #
# ------------------------------------------------------------------ #

def plot_feature_2d(
    real_df: pd.DataFrame,
    synth_df: pd.DataFrame,
    x_feature: str,
    y_feature: str,
    synth_label: str = "Synthetic",
    real_label: str = "Real",
    max_scatter_pts: int = 500,
) -> go.Figure:
    """
    2D distribution comparison for one feature pair.

    Shows KDE contours (Histogram2dContour) plus a subsampled scatter overlay.

    Parameters
    ----------
    real_df, synth_df : pd.DataFrame  — summary feature DataFrames.
    x_feature, y_feature : str        — column names.
    synth_label, real_label : str     — legend labels.
    max_scatter_pts : int             — cap on scatter points to keep plot fast.

    Returns
    -------
    plotly.graph_objects.Figure
    """
    rx = _clean(real_df, [x_feature, y_feature])
    sx = _clean(synth_df, [x_feature, y_feature])

    fig = go.Figure()

    if not rx.empty:
        fig.add_trace(_kde_contour(rx[x_feature].values, rx[y_feature].values, "Blues", real_label))
        pts = rx.sample(min(len(rx), max_scatter_pts), random_state=0)
        fig.add_trace(go.Scatter(
            x=pts[x_feature], y=pts[y_feature],
            mode="markers",
            name=real_label,
            marker=dict(color=_REAL_COLOUR, size=5, line=dict(width=0.5, color=_REAL_LINE)),
            showlegend=True,
        ))

    if not sx.empty:
        fig.add_trace(_kde_contour(sx[x_feature].values, sx[y_feature].values, "Oranges", synth_label))
        pts = sx.sample(min(len(sx), max_scatter_pts), random_state=0)
        fig.add_trace(go.Scatter(
            x=pts[x_feature], y=pts[y_feature],
            mode="markers",
            name=synth_label,
            marker=dict(color=_SYNTH_COLOUR, size=5, line=dict(width=0.5, color=_SYNTH_LINE)),
            showlegend=True,
        ))

    fig.update_layout(
        title=f"{_pretty_label(x_feature)} vs {_pretty_label(y_feature)}",
        xaxis_title=_pretty_label(x_feature),
        yaxis_title=_pretty_label(y_feature),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=450,
        template="plotly_white",
    )
    return fig


def plot_feature_pair_grid(
    real_df: pd.DataFrame,
    synth_df: pd.DataFrame,
    pairs: Optional[List[Tuple[str, str]]] = None,
    synth_label: str = "Synthetic",
    real_label: str = "Real",
) -> go.Figure:
    """
    Grid of 2D distribution comparison subplots, one per feature pair.

    Parameters
    ----------
    pairs : list of (x_feature, y_feature) tuples.
            Defaults to DEFAULT_2D_PAIRS filtered to available columns.

    Returns
    -------
    plotly.graph_objects.Figure
    """
    if pairs is None:
        pairs = DEFAULT_2D_PAIRS

    all_cols = set(real_df.columns) | set(synth_df.columns)
    pairs = [(x, y) for x, y in pairs if x in all_cols and y in all_cols]
    if not pairs:
        return go.Figure().update_layout(title="No valid feature pairs found")

    n = len(pairs)
    ncols = min(2, n)
    nrows = (n + ncols - 1) // ncols

    fig = make_subplots(
        rows=nrows, cols=ncols,
        subplot_titles=[f"{_pretty_label(x)} vs {_pretty_label(y)}" for x, y in pairs],
        horizontal_spacing=0.12,
        vertical_spacing=0.15,
    )

    show_legend = True  # only attach legend entries on first subplot
    for idx, (x_feat, y_feat) in enumerate(pairs):
        row = idx // ncols + 1
        col = idx % ncols + 1

        rx = _clean(real_df, [x_feat, y_feat])
        sx = _clean(synth_df, [x_feat, y_feat])

        if not rx.empty:
            pts = rx.sample(min(len(rx), 300), random_state=0)
            fig.add_trace(go.Scatter(
                x=pts[x_feat], y=pts[y_feat], mode="markers",
                name=real_label,
                marker=dict(color=_REAL_COLOUR, size=5),
                legendgroup="real", showlegend=show_legend,
            ), row=row, col=col)

        if not sx.empty:
            pts = sx.sample(min(len(sx), 300), random_state=0)
            fig.add_trace(go.Scatter(
                x=pts[x_feat], y=pts[y_feat], mode="markers",
                name=synth_label,
                marker=dict(color=_SYNTH_COLOUR, size=5),
                legendgroup="synth", showlegend=show_legend,
            ), row=row, col=col)

        show_legend = False

        fig.update_xaxes(title_text=_pretty_label(x_feat), row=row, col=col)
        fig.update_yaxes(title_text=_pretty_label(y_feat), row=row, col=col)

    fig.update_layout(
        height=400 * nrows,
        title_text="Clinical Feature Distributions (2D)",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


# ------------------------------------------------------------------ #
# Multiple synthetic datasets — 2D                                     #
# ------------------------------------------------------------------ #

def plot_feature_2d_multi(
    real_df: pd.DataFrame,
    synth_dfs: List[pd.DataFrame],
    x_feature: str,
    y_feature: str,
    synth_labels: Optional[List[str]] = None,
    real_label: str = "Real",
    max_scatter_pts: int = 400,
) -> go.Figure:
    """2D scatter for real + multiple synthetic DataFrames."""
    if synth_labels is None:
        synth_labels = [f"Synthetic {i+1}" for i in range(len(synth_dfs))]

    fig = go.Figure()

    rx = _clean(real_df, [x_feature, y_feature])
    if not rx.empty:
        pts = rx.sample(min(len(rx), max_scatter_pts), random_state=0)
        fig.add_trace(go.Scatter(
            x=pts[x_feature], y=pts[y_feature], mode="markers",
            name=real_label, marker=dict(color=_REAL_COLOUR, size=6),
        ))

    for i, (sdf, slbl) in enumerate(zip(synth_dfs, synth_labels)):
        sx = _clean(sdf, [x_feature, y_feature])
        if sx.empty:
            continue
        pts = sx.sample(min(len(sx), max_scatter_pts), random_state=0)
        colour = _MULTI_COLOURS[i % len(_MULTI_COLOURS)]
        fig.add_trace(go.Scatter(
            x=pts[x_feature], y=pts[y_feature], mode="markers",
            name=slbl, marker=dict(color=colour, size=6),
        ))

    fig.update_layout(
        title=f"{_pretty_label(x_feature)} vs {_pretty_label(y_feature)}",
        xaxis_title=_pretty_label(x_feature),
        yaxis_title=_pretty_label(y_feature),
        height=450, template="plotly_white",
    )
    return fig


# ------------------------------------------------------------------ #
# 3D plots                                                             #
# ------------------------------------------------------------------ #

def plot_feature_3d(
    real_df: pd.DataFrame,
    synth_df: pd.DataFrame,
    x_feature: str,
    y_feature: str,
    z_feature: str,
    synth_label: str = "Synthetic",
    real_label: str = "Real",
    max_scatter_pts: int = 600,
) -> go.Figure:
    """
    Interactive 3D scatter comparing real and synthetic feature distributions.

    Parameters
    ----------
    real_df, synth_df : pd.DataFrame
    x_feature, y_feature, z_feature : str  — column names.

    Returns
    -------
    plotly.graph_objects.Figure  (Scatter3d)
    """
    cols = [x_feature, y_feature, z_feature]
    rx = _clean(real_df, cols)
    sx = _clean(synth_df, cols)

    fig = go.Figure()

    if not rx.empty:
        pts = rx.sample(min(len(rx), max_scatter_pts), random_state=0)
        fig.add_trace(go.Scatter3d(
            x=pts[x_feature], y=pts[y_feature], z=pts[z_feature],
            mode="markers",
            name=real_label,
            marker=dict(size=4, color=_REAL_COLOUR, opacity=0.75),
        ))

    if not sx.empty:
        pts = sx.sample(min(len(sx), max_scatter_pts), random_state=0)
        fig.add_trace(go.Scatter3d(
            x=pts[x_feature], y=pts[y_feature], z=pts[z_feature],
            mode="markers",
            name=synth_label,
            marker=dict(size=4, color=_SYNTH_COLOUR, opacity=0.75),
        ))

    fig.update_layout(
        scene=dict(
            xaxis_title=_pretty_label(x_feature),
            yaxis_title=_pretty_label(y_feature),
            zaxis_title=_pretty_label(z_feature),
        ),
        title=(
            f"{_pretty_label(x_feature)} / {_pretty_label(y_feature)} / "
            f"{_pretty_label(z_feature)}"
        ),
        height=550,
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def plot_feature_triple_grid(
    real_df: pd.DataFrame,
    synth_df: pd.DataFrame,
    triples: Optional[List[Tuple[str, str, str]]] = None,
    synth_label: str = "Synthetic",
    real_label: str = "Real",
) -> go.Figure:
    """
    Grid of 3D scatter subplots, one per feature triple.

    Because Plotly does not support 3D scene subplots via make_subplots as
    intuitively as 2D, we stack scenes (scene, scene2, scene3, …) manually.

    Returns
    -------
    plotly.graph_objects.Figure
    """
    if triples is None:
        triples = DEFAULT_3D_TRIPLES

    all_cols = set(real_df.columns) | set(synth_df.columns)
    triples = [(x, y, z) for x, y, z in triples if x in all_cols and y in all_cols and z in all_cols]
    if not triples:
        return go.Figure().update_layout(title="No valid feature triples found")

    n = len(triples)
    ncols = min(2, n)
    nrows = (n + ncols - 1) // ncols

    # Build scenes dict for layout
    scenes = {}
    scene_refs = []
    for i in range(n):
        key = "scene" if i == 0 else f"scene{i+1}"
        row = i // ncols
        col = i % ncols
        scenes[key] = dict(
            xaxis_title=_pretty_label(triples[i][0]),
            yaxis_title=_pretty_label(triples[i][1]),
            zaxis_title=_pretty_label(triples[i][2]),
            domain=dict(
                x=[col / ncols + 0.02, (col + 1) / ncols - 0.02],
                y=[1.0 - (row + 1) / nrows + 0.02, 1.0 - row / nrows - 0.02],
            ),
        )
        scene_refs.append(key)

    fig = go.Figure()
    show_legend = True
    for i, (x_feat, y_feat, z_feat) in enumerate(triples):
        cols = [x_feat, y_feat, z_feat]
        rx = _clean(real_df, cols)
        sx = _clean(synth_df, cols)
        scene_key = scene_refs[i]

        if not rx.empty:
            pts = rx.sample(min(len(rx), 300), random_state=0)
            fig.add_trace(go.Scatter3d(
                x=pts[x_feat], y=pts[y_feat], z=pts[z_feat],
                mode="markers", name=real_label,
                marker=dict(size=3, color=_REAL_COLOUR, opacity=0.75),
                scene=scene_key,
                legendgroup="real", showlegend=show_legend,
            ))

        if not sx.empty:
            pts = sx.sample(min(len(sx), 300), random_state=0)
            fig.add_trace(go.Scatter3d(
                x=pts[x_feat], y=pts[y_feat], z=pts[z_feat],
                mode="markers", name=synth_label,
                marker=dict(size=3, color=_SYNTH_COLOUR, opacity=0.75),
                scene=scene_key,
                legendgroup="synth", showlegend=show_legend,
            ))

        show_legend = False

    layout_update = dict(
        title_text="Clinical Feature Distributions (3D)",
        height=max(500, 500 * nrows),
        template="plotly_white",
        **scenes,
    )
    fig.update_layout(**layout_update)
    return fig
