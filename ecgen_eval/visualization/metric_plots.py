"""
Plotly-based plots for metric results.

Provides:
  - Per-lead bar chart
  - Distribution violin (for DTW pairwise distances and per-pair metric values)
  - PSD overlay and amplitude-histogram overlay
  - Radar chart summarising all metrics across datasets
"""

from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ecgen_eval.metrics.base import MetricResult
from ecgen_eval.visualization.ecg_paper import SYNTH_PALETTE, get_synth_color


# ------------------------------------------------------------------ #
# Per-lead bar chart                                                   #
# ------------------------------------------------------------------ #

def plot_per_lead_bar(
    results: Dict[str, MetricResult],
    metric_name: str,
    lead_names: Optional[List[str]] = None,
) -> go.Figure:
    """
    Grouped bar chart: X = leads, bars = synthetic datasets.

    Parameters
    ----------
    results : dict mapping dataset_label → MetricResult
    metric_name : str   (e.g. "MMD", "DTW")
    lead_names : list of str, optional — filter/order leads
    """
    fig = go.Figure()

    for i, (label, result) in enumerate(results.items()):
        per_lead = result.per_lead_scores
        if lead_names is None:
            leads = list(per_lead.keys())
        else:
            leads = [l for l in lead_names if l in per_lead]

        fig.add_trace(
            go.Bar(
                name=label,
                x=leads,
                y=[per_lead[l] for l in leads],
                marker_color=get_synth_color(i),
                opacity=0.85,
            )
        )

    direction = "lower" if not list(results.values())[0].higher_is_better else "higher"
    fig.update_layout(
        title=f"{metric_name} Score per Lead ({direction} = better)",
        xaxis_title="Lead",
        yaxis_title=f"{metric_name} Score",
        barmode="group",
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="rgba(200,200,200,0.5)"),
    )
    return fig


# ------------------------------------------------------------------ #
# Violin plot for pairwise distance distributions                      #
# ------------------------------------------------------------------ #

def plot_metric_violin(
    results: Dict[str, MetricResult],
    metric_name: str,
    dist_key: str = "per_lead_all_distances",
    leads: Optional[List[str]] = None,
) -> go.Figure:
    """
    Violin plot showing the distribution of pairwise distances per lead.
    Only meaningful for metrics that store per-pair distance lists in extra[dist_key].

    Parameters
    ----------
    results : dict mapping dataset_label → MetricResult
    metric_name : str
    dist_key : str — key in MetricResult.extra that holds {lead: [distances]}
    leads : list of str, optional
    """
    # Check if data is available
    sample_result = next(iter(results.values()))
    what = "Pairwise Distance"
    if dist_key not in sample_result.extra and "per_lead_all_values" in sample_result.extra:
        # Pairwise metrics (mse, pearson, ...) store one value per matched pair.
        dist_key, what = "per_lead_all_values", "Per-pair Value"
    if dist_key not in sample_result.extra:
        return _empty_figure(f"No per-pair distances available for {metric_name}")

    all_leads = list(next(iter(results.values())).extra[dist_key].keys())
    if leads:
        all_leads = [l for l in leads if l in all_leads]

    n_cols = min(4, len(all_leads))
    n_rows = (len(all_leads) + n_cols - 1) // n_cols

    fig = make_subplots(
        rows=n_rows,
        cols=n_cols,
        subplot_titles=all_leads,
        vertical_spacing=0.12,
        horizontal_spacing=0.06,
    )

    for li, lead in enumerate(all_leads):
        row = li // n_cols + 1
        col = li % n_cols + 1
        for si, (label, result) in enumerate(results.items()):
            dists = result.extra.get(dist_key, {}).get(lead, [])
            if not dists:
                continue
            fig.add_trace(
                go.Violin(
                    y=dists,
                    name=label,
                    legendgroup=label,
                    showlegend=(li == 0),
                    line_color=get_synth_color(si),
                    fillcolor=get_synth_color(si),
                    opacity=0.6,
                    box_visible=True,
                    meanline_visible=True,
                    points=False,
                ),
                row=row, col=col,
            )

    fig.update_layout(
        title=f"{metric_name} {what} Distribution per Lead",
        height=280 * n_rows + 80,
        violinmode="group",
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_yaxes(gridcolor="rgba(200,200,200,0.5)", zeroline=False)
    return fig


# ------------------------------------------------------------------ #
# Radar chart (all metrics)                                            #
# ------------------------------------------------------------------ #

def plot_radar_chart(
    scores_by_dataset: Dict[str, Dict[str, float]],
    metric_names: Optional[List[str]] = None,
    higher_is_better: Optional[Dict[str, bool]] = None,
) -> go.Figure:
    """
    Radar (spider) chart with one polygon per synthetic dataset.
    Scores are normalised so that the outer edge = best.

    Parameters
    ----------
    scores_by_dataset : {dataset_label: {metric_name: score}}
    metric_names : order of metrics on radar axes
    higher_is_better : {metric_name: bool}
    """
    if metric_names is None:
        metric_names = sorted(
            {m for s in scores_by_dataset.values() for m in s}
        )

    if higher_is_better is None:
        higher_is_better = {}

    # Normalise: map each metric to [0, 1] where 1 = best
    norm_scores: Dict[str, Dict[str, float]] = {ds: {} for ds in scores_by_dataset}

    for metric in metric_names:
        vals = {
            ds: scores_by_dataset[ds].get(metric, np.nan)
            for ds in scores_by_dataset
        }
        valid = [v for v in vals.values() if not np.isnan(v)]
        if not valid:
            continue
        lo, hi = min(valid), max(valid)
        span = (hi - lo) or 1.0

        hib = higher_is_better.get(metric, False)
        for ds, v in vals.items():
            if np.isnan(v):
                norm_scores[ds][metric] = 0.0
            elif hib:
                norm_scores[ds][metric] = (v - lo) / span
            else:
                norm_scores[ds][metric] = 1.0 - (v - lo) / span

    fig = go.Figure()
    for si, (label, scores) in enumerate(norm_scores.items()):
        r_vals = [scores.get(m, 0.0) for m in metric_names]
        r_vals_closed = r_vals + [r_vals[0]]
        theta_closed = metric_names + [metric_names[0]]
        fig.add_trace(
            go.Scatterpolar(
                r=r_vals_closed,
                theta=theta_closed,
                fill="toself",
                name=label,
                line_color=get_synth_color(si),
                fillcolor=get_synth_color(si),
                opacity=0.4,
            )
        )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1], tickfont_size=9),
            angularaxis=dict(tickfont_size=11),
            bgcolor="white",
        ),
        showlegend=True,
        title="Metric Summary Radar (outer edge = best quality)",
        height=500,
        paper_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
    )
    return fig


# ------------------------------------------------------------------ #
# PSD overlay plot                                                     #
# ------------------------------------------------------------------ #

def plot_psd_overlay(
    results: Dict[str, MetricResult],
    fs: float = 500.0,
    leads: Optional[List[str]] = None,
    max_freq_hz: float = 40.0,
) -> go.Figure:
    """
    Overlay the mean normalised PSD of real vs. synthetic datasets per lead.

    Only meaningful for PSDMetric results which store mean PSDs in
    ``result.extra["per_lead_psd_real"]`` and ``result.extra["per_lead_psd_synth"]``.

    Parameters
    ----------
    results : dict  dataset_label → MetricResult
    fs : float      sampling frequency (used to build frequency axis)
    leads : list of str, optional
    max_freq_hz : float   clip display to this frequency (default 40 Hz)
    """
    sample_result = next(iter(results.values()))
    if "per_lead_psd_real" not in sample_result.extra:
        return _empty_figure("PSD data not available (run PSDMetric first)")

    all_leads = list(sample_result.extra["per_lead_psd_real"].keys())
    if leads:
        all_leads = [l for l in leads if l in all_leads]

    n_cols = min(4, len(all_leads))
    n_rows = (len(all_leads) + n_cols - 1) // n_cols

    fig = make_subplots(
        rows=n_rows, cols=n_cols,
        subplot_titles=all_leads,
        vertical_spacing=0.14,
        horizontal_spacing=0.06,
    )

    for li, lead in enumerate(all_leads):
        row = li // n_cols + 1
        col = li % n_cols + 1

        # Build frequency axis from PSD length
        psd_r_first = np.array(sample_result.extra["per_lead_psd_real"][lead])
        n_freqs = len(psd_r_first)
        freqs = np.linspace(0, fs / 2, n_freqs)
        freq_mask = freqs <= max_freq_hz

        # Real (use first result's real PSD — same for all synthetic comparisons)
        psd_real = np.array(sample_result.extra["per_lead_psd_real"][lead])
        fig.add_trace(
            go.Scatter(
                x=freqs[freq_mask].tolist(),
                y=psd_real[freq_mask].tolist(),
                name="Real",
                legendgroup="real",
                showlegend=(li == 0),
                line=dict(color="black", width=2),
                mode="lines",
            ),
            row=row, col=col,
        )

        for si, (label, result) in enumerate(results.items()):
            psd_synth = np.array(result.extra["per_lead_psd_synth"].get(lead, []))
            if len(psd_synth) == 0:
                continue
            fig.add_trace(
                go.Scatter(
                    x=freqs[freq_mask].tolist(),
                    y=psd_synth[freq_mask].tolist(),
                    name=label,
                    legendgroup=label,
                    showlegend=(li == 0),
                    line=dict(color=get_synth_color(si), width=1.5, dash="dash"),
                    mode="lines",
                    opacity=0.8,
                ),
                row=row, col=col,
            )

    fig.update_layout(
        title=f"Mean Normalised PSD per Lead (0–{max_freq_hz:.0f} Hz)",
        height=280 * n_rows + 80,
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(title_text="Frequency (Hz)", gridcolor="rgba(200,200,200,0.5)")
    fig.update_yaxes(title_text="Normalised Power", gridcolor="rgba(200,200,200,0.5)")
    return fig


# ------------------------------------------------------------------ #
# Amplitude histogram overlay (js_div metric)                          #
# ------------------------------------------------------------------ #

def plot_amplitude_hist(
    results: Dict[str, MetricResult],
    leads: Optional[List[str]] = None,
) -> go.Figure:
    """
    Overlay the amplitude-value distributions of real vs. synthetic datasets per lead.

    Only meaningful for AmplitudeJSMetric (``js_div``) results, which store the
    histograms in ``result.extra["per_lead_hist_real"]`` / ``["per_lead_hist_synth"]``
    and the bin edges in ``result.extra["bin_edges"]``. The two open-ended tail bins
    are drawn at the first and last edge.

    Parameters
    ----------
    results : dict  dataset_label → MetricResult
    leads : list of str, optional
    """
    sample_result = next(iter(results.values()))
    if "per_lead_hist_real" not in sample_result.extra:
        return _empty_figure("Amplitude histograms not available (run the js_div metric first)")

    all_leads = list(sample_result.extra["per_lead_hist_real"].keys())
    if leads:
        all_leads = [l for l in leads if l in all_leads]

    n_cols = min(4, len(all_leads))
    n_rows = (len(all_leads) + n_cols - 1) // n_cols
    fig = make_subplots(
        rows=n_rows, cols=n_cols, subplot_titles=all_leads,
        vertical_spacing=0.14, horizontal_spacing=0.06,
    )

    for li, lead in enumerate(all_leads):
        row = li // n_cols + 1
        col = li % n_cols + 1
        edges = np.array(sample_result.extra["bin_edges"][lead])
        width = edges[1] - edges[0]
        # Bin centres; the two tail bins sit half a bin outside the finite range.
        x = np.concatenate([[edges[0] - width / 2], 0.5 * (edges[:-1] + edges[1:]),
                            [edges[-1] + width / 2]])
        fig.add_trace(
            go.Scatter(
                x=x.tolist(), y=sample_result.extra["per_lead_hist_real"][lead],
                name="Real", legendgroup="real", showlegend=(li == 0),
                line=dict(color="black", width=2, shape="hvh"), mode="lines",
            ),
            row=row, col=col,
        )
        for si, (label, result) in enumerate(results.items()):
            hist = result.extra["per_lead_hist_synth"].get(lead, [])
            if len(hist) == 0:
                continue
            fig.add_trace(
                go.Scatter(
                    x=x.tolist(), y=hist, name=label, legendgroup=label,
                    showlegend=(li == 0), mode="lines", opacity=0.8,
                    line=dict(color=get_synth_color(si), width=1.5, dash="dash", shape="hvh"),
                ),
                row=row, col=col,
            )

    fig.update_layout(
        title="Amplitude Distribution per Lead (outermost bins collect out-of-range values)",
        height=280 * n_rows + 80,
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(title_text="Amplitude", gridcolor="rgba(200,200,200,0.5)")
    fig.update_yaxes(title_text="Share of samples", gridcolor="rgba(200,200,200,0.5)")
    return fig


# ------------------------------------------------------------------ #
# Helper                                                               #
# ------------------------------------------------------------------ #

def _empty_figure(msg: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=msg, xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
    fig.update_layout(height=200)
    return fig
