"""
Beat-level morphology plots: R-peak-aligned beats summarised as quantile bands or
density maps.

Showing a few hand-picked recordings is the most common "visual inspection" in the
literature, and the least reproducible. These plots summarise *every* detected beat
of a dataset instead, so the comparison does not depend on which samples were picked.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ecgen_eval.data.dataset import ECGDataset
from ecgen_eval.visualization.ecg_paper import get_synth_color

_REAL_RGB = "10, 10, 10"


def _reference_lead(dataset: ECGDataset, ref_lead: Optional[str]) -> int:
    if ref_lead is not None and ref_lead in dataset.lead_names:
        return dataset.lead_names.index(ref_lead)
    return dataset.lead_names.index("II") if "II" in dataset.lead_names else 0


def aligned_beats_by_lead(
    dataset: ECGDataset,
    leads: Optional[Sequence[str]] = None,
    pre_ms: float = 250.0,
    post_ms: float = 450.0,
    max_beats: int = 5000,
    max_recordings: int = 500,
    ref_lead: Optional[str] = None,
    seed: int = 42,
) -> Tuple[Dict[str, np.ndarray], Dict[str, int]]:
    """
    Cut R-peak-aligned beats out of every requested lead.

    R peaks are detected once per recording on a reference lead (``ref_lead``, else
    lead II, else the first lead) and reused for all leads, so the leads stay
    time-aligned. Beats whose window crosses the recording edge are dropped.

    Returns
    -------
    beats : {lead: (n_beats, n_samples) array}, R peak at sample ``round(pre_ms·fs/1000)``
    stats : {'n_recordings', 'n_recordings_without_beats', 'n_beats'}
    """
    from ecgen_eval.metrics._rpeaks import detect_r_peaks

    leads = [ld for ld in (leads or dataset.lead_names) if ld in dataset.lead_names]
    fs = float(dataset.fs)
    pre = int(round(pre_ms * fs / 1000.0))
    post = int(round(post_ms * fs / 1000.0))
    width = pre + post
    data = dataset.data
    n_rec, _, T = data.shape

    rng = np.random.default_rng(seed)
    rec_idx = np.arange(n_rec)
    if n_rec > max_recordings:
        rec_idx = np.sort(rng.choice(n_rec, size=max_recordings, replace=False))

    ref = _reference_lead(dataset, ref_lead)
    windows: List[Tuple[int, int]] = []  # (recording, start sample)
    n_without = 0
    for ri in rec_idx:
        peaks = detect_r_peaks(data[ri, ref], fs)
        peaks = [int(p) for p in peaks if p - pre >= 0 and p + post <= T]
        if not peaks:
            n_without += 1
        windows.extend((int(ri), p - pre) for p in peaks)

    if len(windows) > max_beats:
        keep = np.sort(rng.choice(len(windows), size=max_beats, replace=False))
        windows = [windows[k] for k in keep]

    beats: Dict[str, np.ndarray] = {}
    for lead in leads:
        li = dataset.lead_names.index(lead)
        if windows:
            beats[lead] = np.stack([data[ri, li, s:s + width] for ri, s in windows]).astype(
                np.float64
            )
        else:
            beats[lead] = np.empty((0, width))
    stats = {
        "n_recordings": int(len(rec_idx)),
        "n_recordings_without_beats": int(n_without),
        "n_beats": int(len(windows)),
    }
    return beats, stats


def extract_aligned_beats(
    dataset: ECGDataset,
    lead: str,
    pre_ms: float = 250.0,
    post_ms: float = 450.0,
    max_beats: int = 5000,
    seed: int = 42,
) -> np.ndarray:
    """
    R-peak-aligned beats of one lead.

    Returns
    -------
    (n_beats, n_samples) array; the R peak sits at sample ``round(pre_ms·fs/1000)``.
    """
    if lead not in dataset.lead_names:
        raise ValueError(f"Lead {lead!r} not in dataset ({dataset.lead_names}).")
    beats, _ = aligned_beats_by_lead(
        dataset, [lead], pre_ms, post_ms, max_beats=max_beats, ref_lead=lead, seed=seed
    )
    return beats[lead]


def plot_beat_bands(
    real: ECGDataset,
    synthetics: List[ECGDataset],
    leads: Optional[List[str]] = None,
    quantiles: Tuple[float, float, float] = (0.05, 0.5, 0.95),
    pre_ms: float = 250.0,
    post_ms: float = 450.0,
    mode: str = "bands",
    max_beats: int = 5000,
    seed: int = 42,
) -> go.Figure:
    """
    Compare beat morphology of real and synthetic datasets over all detected beats.

    Parameters
    ----------
    real : ECGDataset
    synthetics : list of ECGDataset
    leads : list of str, optional — defaults to all leads of the real dataset
    quantiles : (low, mid, high) — band limits and centre line. Default: 5 %, median, 95 %.
    pre_ms, post_ms : window before / after the R peak
    mode : 'bands' (median line + shaded quantile band per dataset, one subplot per
        lead) or 'density' (time × amplitude histogram, one row per lead and one
        column per dataset)
    max_beats : cap on beats per dataset
    seed : random seed for subsampling

    Returns
    -------
    go.Figure — a placeholder figure with a message if no beat was detected in the
    real dataset.
    """
    if mode not in ("bands", "density"):
        raise ValueError(f"Unknown mode: {mode!r}. Choose 'bands' or 'density'.")
    leads = [ld for ld in (leads or real.lead_names) if ld in real.lead_names]
    if not leads:
        raise ValueError("No valid lead names found in real dataset.")

    datasets = [real] + list(synthetics)
    colors = [f"rgb({_REAL_RGB})"] + [get_synth_color(i) for i in range(len(synthetics))]
    all_beats = []
    all_stats = []
    for ds in datasets:
        beats, stats = aligned_beats_by_lead(
            ds, leads, pre_ms, post_ms, max_beats=max_beats, seed=seed
        )
        all_beats.append(beats)
        all_stats.append(stats)

    if all_stats[0]["n_beats"] == 0:
        return _message_figure(
            f"No beats detected in {real.label}: R-peak detection found nothing to align."
        )

    labels = [
        f"{ds.label} ({st['n_beats']} beats)" for ds, st in zip(datasets, all_stats)
    ]
    width = next(iter(all_beats[0].values())).shape[1]
    t_ms = (np.arange(width) - int(round(pre_ms * real.fs / 1000.0))) * 1000.0 / real.fs

    if mode == "bands":
        fig = _bands(all_beats, labels, colors, leads, quantiles, t_ms)
    else:
        fig = _density(all_beats, labels, leads, t_ms)
    return fig


# ------------------------------------------------------------------ #
# Mode implementations                                                 #
# ------------------------------------------------------------------ #

def _bands(all_beats, labels, colors, leads, quantiles, t_ms) -> go.Figure:
    lo_q, mid_q, hi_q = quantiles
    n_cols = min(4, len(leads))
    n_rows = (len(leads) + n_cols - 1) // n_cols
    fig = make_subplots(
        rows=n_rows, cols=n_cols, subplot_titles=leads,
        vertical_spacing=0.14 if n_rows > 1 else 0.1, horizontal_spacing=0.06,
    )
    x = t_ms.tolist()
    for li, lead in enumerate(leads):
        row, col = li // n_cols + 1, li % n_cols + 1
        for di, (beats, label, color) in enumerate(zip(all_beats, labels, colors)):
            b = beats.get(lead)
            if b is None or b.shape[0] == 0:
                continue
            lo, mid, hi = np.quantile(b, [lo_q, mid_q, hi_q], axis=0)
            fill = color.replace("rgb(", "rgba(").replace(")", ", 0.18)")
            group = f"ds_{di}"
            fig.add_trace(go.Scatter(
                x=x, y=hi.tolist(), mode="lines", line=dict(width=0), hoverinfo="skip",
                legendgroup=group, showlegend=False,
            ), row=row, col=col)
            fig.add_trace(go.Scatter(
                x=x, y=lo.tolist(), mode="lines", line=dict(width=0), fill="tonexty",
                fillcolor=fill, hoverinfo="skip", legendgroup=group, showlegend=False,
            ), row=row, col=col)
            fig.add_trace(go.Scatter(
                x=x, y=mid.tolist(), mode="lines", name=label, legendgroup=group,
                showlegend=(li == 0), line=dict(color=color, width=1.8),
                hovertemplate="<b>%{fullData.name}</b><br>%{x:.0f} ms<br>%{y:.3f} mV"
                              "<extra></extra>",
            ), row=row, col=col)
    fig.update_layout(
        title=(f"Beat morphology — line: {_pct(mid_q)} quantile, band: "
               f"{_pct(lo_q)}–{_pct(hi_q)} of R-peak-aligned beats"),
        height=260 * n_rows + 90, plot_bgcolor="white", paper_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(title_text="Time from R peak (ms)", gridcolor="rgba(200,200,200,0.5)",
                     zeroline=True, zerolinecolor="rgba(120,120,120,0.6)")
    fig.update_yaxes(title_text="mV", gridcolor="rgba(200,200,200,0.5)")
    return fig


def _density(all_beats, labels, leads, t_ms) -> go.Figure:
    n_rows, n_cols = len(leads), len(all_beats)
    fig = make_subplots(
        rows=n_rows, cols=n_cols, column_titles=labels, row_titles=leads,
        shared_xaxes=True, vertical_spacing=0.04, horizontal_spacing=0.04,
    )
    step = t_ms[1] - t_ms[0] if len(t_ms) > 1 else 1.0
    for ri, lead in enumerate(leads, start=1):
        real_b = all_beats[0][lead]
        lo, hi = np.percentile(real_b, [0.5, 99.5])
        pad = 0.15 * (hi - lo + 1e-9)
        y_edges = np.linspace(lo - pad, hi + pad, 81)
        y_mid = 0.5 * (y_edges[:-1] + y_edges[1:])
        for ci, beats in enumerate(all_beats, start=1):
            b = beats.get(lead)
            if b is None or b.shape[0] == 0:
                continue
            # One amplitude histogram per time sample -> (n_amp_bins, n_time)
            idx = np.clip(np.searchsorted(y_edges, b, side="right") - 1, 0, len(y_mid) - 1)
            z = np.zeros((len(y_mid), b.shape[1]))
            np.add.at(z, (idx, np.broadcast_to(np.arange(b.shape[1]), b.shape)), 1.0)
            z /= b.shape[0]
            fig.add_trace(go.Heatmap(
                x=t_ms.tolist(), y=y_mid.tolist(), z=z.tolist(), dx=step,
                colorscale="Viridis", showscale=False, zmin=0, zmax=float(np.quantile(z, 0.995)),
                hovertemplate="%{x:.0f} ms<br>%{y:.3f} mV<br>share of beats %{z:.3f}"
                              "<extra></extra>",
            ), row=ri, col=ci)
    fig.update_layout(
        title="Beat density — share of R-peak-aligned beats at each time and amplitude",
        height=200 * n_rows + 110, plot_bgcolor="white", paper_bgcolor="white",
    )
    fig.update_xaxes(title_text="Time from R peak (ms)", row=n_rows)
    return fig


def _pct(q: float) -> str:
    return "median" if abs(q - 0.5) < 1e-9 else f"{100 * q:g} %"


def _message_figure(msg: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=msg, xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
    fig.update_layout(height=200)
    return fig
