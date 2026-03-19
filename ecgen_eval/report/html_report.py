"""
Self-contained interactive HTML report generator.

Produces a single .html file embedding all Plotly figures, metric tables,
citations, and ECG sample galleries.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

import numpy as np
import plotly.graph_objects as go

from ecgen_eval.data.dataset import ECGDataset
from ecgen_eval.metrics.base import MetricResult
from ecgen_eval.visualization.ecg_waveform import plot_ecg_comparison
from ecgen_eval.visualization.metric_plots import (
    plot_per_lead_bar,
    plot_metric_violin,
    plot_psd_overlay,
    plot_radar_chart,
)


# ------------------------------------------------------------------ #
# Public API                                                           #
# ------------------------------------------------------------------ #

def generate_report(
    real: ECGDataset,
    synthetics: List[ECGDataset],
    metric_results: Dict[str, Dict[str, MetricResult]],
    output_path: Union[str, Path],
    n_ecg_samples: int = 3,
    leads: Optional[List[str]] = None,
    compare_mode: str = "overlay",
    plotly_cdn: bool = True,
    fs: float = 500.0,
) -> Path:
    """
    Build and write a self-contained HTML report.

    Parameters
    ----------
    real : ECGDataset
    synthetics : list of ECGDataset
    metric_results : {metric_name: {synth_label: MetricResult}}
    output_path : str or Path
    n_ecg_samples : int — number of ECG recordings to show in gallery
    leads : list of str, optional — subset of leads to show in ECG gallery
    compare_mode : 'overlay' | 'sidebyside' | 'grid'
    plotly_cdn : bool — if True, load Plotly.js from CDN (smaller HTML);
                        if False, embed full JS (offline-capable).

    Returns
    -------
    Path to the written HTML file.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    include_js = "cdn" if plotly_cdn else True

    sections: List[str] = []

    # 1. Header / summary
    sections.append(_render_header(real, synthetics))

    # 2. Dataset summary table
    sections.append(_render_dataset_table(real, synthetics))

    # 3. ECG Sample Gallery
    sections.append(_render_ecg_gallery(
        real, synthetics, n_ecg_samples, leads, compare_mode, include_js
    ))

    # 4. Metric sections
    for metric_name, by_synth in metric_results.items():
        sections.append(_render_metric_section(
            metric_name, by_synth, real.lead_names, include_js,
            fs=fs,
        ))

    # 5. Radar summary (if multiple metrics)
    if len(metric_results) > 1:
        sections.append(_render_radar(metric_results, include_js))

    # 6. Citations
    sections.append(_render_citations(metric_results))

    html = _wrap_html(
        title=f"ECGEN-Eval Report — {real.label}",
        body="\n".join(sections),
        plotly_cdn=plotly_cdn,
    )

    output_path.write_text(html, encoding="utf-8")
    return output_path


# ------------------------------------------------------------------ #
# Section renderers                                                    #
# ------------------------------------------------------------------ #

def _render_header(real: ECGDataset, synthetics: List[ECGDataset]) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    synth_labels = ", ".join(f"<em>{s.label}</em>" for s in synthetics)
    return f"""
<div class="section header-section">
  <h1>ECGEN-Eval Report</h1>
  <p class="subtitle">
    Synthetic ECG Quality Evaluation &mdash;
    Real: <strong>{real.label}</strong> &nbsp;|&nbsp;
    Synthetic: {synth_labels}
  </p>
  <p class="meta">
    Generated: {ts} &nbsp;|&nbsp;
    ecgen-eval v0.1.0
  </p>
</div>
"""


def _render_dataset_table(real: ECGDataset, synthetics: List[ECGDataset]) -> str:
    rows = ""
    for ds, kind in [(real, "Real")] + [(s, "Synthetic") for s in synthetics]:
        badge_cls = "badge-real" if kind == "Real" else "badge-synth"
        rows += f"""
    <tr>
      <td><span class="badge {badge_cls}">{kind}</span></td>
      <td><strong>{ds.label}</strong></td>
      <td>{ds.n_samples}</td>
      <td>{ds.n_leads}</td>
      <td>{ds.n_timepoints}</td>
      <td>{ds.fs} Hz</td>
      <td>{ds.duration_sec:.1f} s</td>
      <td>{", ".join(ds.lead_names)}</td>
    </tr>"""

    return f"""
<div class="section">
  <h2>Dataset Summary</h2>
  <table class="summary-table">
    <thead>
      <tr>
        <th>Type</th><th>Label</th><th>Samples</th><th>Leads</th>
        <th>Timepoints</th><th>Fs</th><th>Duration</th><th>Lead Names</th>
      </tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
</div>
"""


def _render_ecg_gallery(
    real: ECGDataset,
    synthetics: List[ECGDataset],
    n_samples: int,
    leads: Optional[List[str]],
    mode: str,
    include_js,
) -> str:
    n_samples = min(n_samples, real.n_samples)
    plots_html = ""
    for i in range(n_samples):
        fig = plot_ecg_comparison(
            real=real,
            synthetics=synthetics,
            sample_index=i,
            leads=leads,
            mode=mode,
            add_calibration_pulse=True,
        )
        plots_html += f'<div class="ecg-sample"><h4>Sample {i}</h4>'
        plots_html += fig.to_html(
            full_html=False,
            include_plotlyjs=include_js if i == 0 else False,
            div_id=f"ecg_sample_{i}",
            config={"responsive": True, "displayModeBar": True},
        )
        plots_html += "</div>"
        include_js = False  # only embed JS once

    return f"""
<div class="section">
  <h2>ECG Sample Gallery</h2>
  <p class="hint">
    Comparison mode: <code>{mode}</code> &nbsp;|&nbsp;
    Calibration pulse: 1 mV &times; 0.2 s prepended &nbsp;|&nbsp;
    Paper: 25 mm/s &middot; 10 mm/mV
  </p>
  {plots_html}
</div>
"""


def _render_metric_section(
    metric_name: str,
    by_synth: Dict[str, MetricResult],
    lead_names: List[str],
    include_js,
    fs: float = 500.0,
) -> str:
    # Pick first result for description/reference
    sample = next(iter(by_synth.values()))

    # Score table
    score_rows = ""
    for label, result in by_synth.items():
        score_rows += f"<tr><td>{label}</td><td><strong>{result.score:.6f}</strong></td></tr>"

    table = f"""
  <table class="metric-table">
    <thead><tr><th>Dataset</th><th>Score</th></tr></thead>
    <tbody>{score_rows}</tbody>
  </table>
  <p class="hint">{"Higher is better." if sample.higher_is_better else "Lower is better (0 = identical distributions)."}</p>
"""

    # Per-lead bar chart
    bar_fig = plot_per_lead_bar(by_synth, metric_name.upper(), lead_names)
    bar_html = bar_fig.to_html(
        full_html=False,
        include_plotlyjs=False,
        config={"responsive": True},
    )

    # Violin (DTW pairwise distances)
    violin_html = ""
    violin_fig = plot_metric_violin(by_synth, metric_name.upper())
    if violin_fig.data:
        violin_html = violin_fig.to_html(
            full_html=False,
            include_plotlyjs=False,
            config={"responsive": True},
        )

    # PSD overlay (PSD metric)
    psd_html = ""
    if metric_name.lower() == "psd":
        psd_fig = plot_psd_overlay(by_synth, fs=fs)
        if psd_fig.data:
            psd_html = psd_fig.to_html(
                full_html=False,
                include_plotlyjs=False,
                config={"responsive": True},
            )

    return f"""
<div class="section metric-section">
  <h2>{metric_name.upper()} — {sample.description}</h2>
  <div class="metric-meta">
    <strong>Reference:</strong> <span class="citation">{sample.reference}</span>
  </div>
  {table}
  <div class="plot-row">
    {bar_html}
    {violin_html}
  </div>
  {psd_html}
</div>
"""


def _render_radar(
    metric_results: Dict[str, Dict[str, MetricResult]],
    include_js,
) -> str:
    # Collect {synth_label: {metric: score}}
    scores_by_dataset: Dict[str, Dict[str, float]] = {}
    hib_map: Dict[str, bool] = {}

    for metric_name, by_synth in metric_results.items():
        hib_map[metric_name] = next(iter(by_synth.values())).higher_is_better
        for label, result in by_synth.items():
            scores_by_dataset.setdefault(label, {})[metric_name] = result.score

    radar_fig = plot_radar_chart(scores_by_dataset, higher_is_better=hib_map)
    radar_html = radar_fig.to_html(
        full_html=False,
        include_plotlyjs=False,
        config={"responsive": True},
    )
    return f"""
<div class="section">
  <h2>Overall Quality Summary</h2>
  <p class="hint">
    Radar chart: each axis is one metric, normalised so the outer ring = best quality.
  </p>
  {radar_html}
</div>
"""


def _render_citations(metric_results: Dict[str, Dict[str, MetricResult]]) -> str:
    seen = set()
    items = ""
    for metric_name, by_synth in metric_results.items():
        result = next(iter(by_synth.values()))
        if result.reference and result.reference not in seen:
            seen.add(result.reference)
            items += f"<li><strong>{metric_name.upper()}:</strong> {result.reference}</li>"

    return f"""
<div class="section citations-section">
  <h2>References</h2>
  <ul class="citations">{items}</ul>
</div>
"""


# ------------------------------------------------------------------ #
# HTML skeleton                                                         #
# ------------------------------------------------------------------ #

def _wrap_html(title: str, body: str, plotly_cdn: bool) -> str:
    cdn_tag = (
        '<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>'
        if plotly_cdn
        else ""
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{title}</title>
  {cdn_tag}
  <style>
    *, *::before, *::after {{ box-sizing: border-box; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #f8f9fa;
      color: #212529;
      margin: 0;
      padding: 0;
    }}
    .container {{
      max-width: 1400px;
      margin: 0 auto;
      padding: 24px 32px;
    }}
    .section {{
      background: #ffffff;
      border-radius: 10px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
      padding: 28px 32px;
      margin-bottom: 28px;
    }}
    .header-section {{
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
      color: #fff;
    }}
    .header-section h1 {{
      margin: 0 0 8px;
      font-size: 2.2rem;
      font-weight: 700;
      letter-spacing: -0.5px;
    }}
    .subtitle {{ font-size: 1.05rem; margin: 0 0 8px; opacity: 0.9; }}
    .meta {{ font-size: 0.85rem; opacity: 0.65; margin: 0; }}
    h2 {{
      font-size: 1.35rem;
      font-weight: 600;
      margin: 0 0 16px;
      color: #1a1a2e;
      border-bottom: 2px solid #e9ecef;
      padding-bottom: 8px;
    }}
    h4 {{ margin: 16px 0 8px; font-size: 1rem; color: #495057; }}
    .hint {{ font-size: 0.88rem; color: #6c757d; margin: 0 0 16px; }}
    code {{ background: #f1f3f5; padding: 2px 6px; border-radius: 4px; font-size: 0.85em; }}
    .summary-table, .metric-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.9rem;
      margin-bottom: 12px;
    }}
    .summary-table th, .metric-table th {{
      background: #f1f3f5;
      padding: 10px 12px;
      text-align: left;
      font-weight: 600;
      border-bottom: 2px solid #dee2e6;
    }}
    .summary-table td, .metric-table td {{
      padding: 9px 12px;
      border-bottom: 1px solid #f1f3f5;
      vertical-align: middle;
    }}
    .summary-table tr:hover td, .metric-table tr:hover td {{
      background: #f8f9fa;
    }}
    .badge {{
      display: inline-block;
      padding: 3px 10px;
      border-radius: 12px;
      font-size: 0.78rem;
      font-weight: 600;
    }}
    .badge-real  {{ background: #d0f0c0; color: #1a5c2a; }}
    .badge-synth {{ background: #cce5ff; color: #004085; }}
    .metric-section .metric-meta {{
      font-size: 0.85rem;
      color: #6c757d;
      background: #f8f9fa;
      border-left: 4px solid #0f3460;
      padding: 10px 14px;
      border-radius: 0 6px 6px 0;
      margin-bottom: 16px;
    }}
    .citation {{ font-style: italic; }}
    .plot-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
    }}
    .plot-row > div {{ flex: 1 1 400px; }}
    .citations-section ul.citations {{
      font-size: 0.88rem;
      line-height: 1.7;
      color: #495057;
    }}
    .ecg-sample {{ margin-bottom: 24px; }}
  </style>
</head>
<body>
  <div class="container">
    {body}
    <div style="text-align:center; font-size:0.8rem; color:#adb5bd; padding: 24px 0 8px;">
      Generated by <strong>ecgen-eval</strong> v0.1.0 &nbsp;&mdash;&nbsp;
      <a href="https://github.com/vlbthambawita/ECGEN-Eval" style="color:#adb5bd;">GitHub</a>
    </div>
  </div>
</body>
</html>"""
