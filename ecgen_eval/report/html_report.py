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
    plot_amplitude_hist,
    plot_radar_chart,
)
from ecgen_eval.visualization.beat_plots import plot_beat_bands
from ecgen_eval.visualization.feature_plots import (
    plot_feature_pair_grid,
    plot_feature_triple_grid,
    DEFAULT_2D_PAIRS,
    DEFAULT_3D_TRIPLES,
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
    feature_df_real=None,
    feature_dfs_synth=None,
    feature_plots_2d: bool = False,
    feature_plots_3d: bool = False,
    beat_bands: bool = True,
    embedding_plots: Optional[List[go.Figure]] = None,
    gallery_selection: str = "first",
    gallery_seed: int = 42,
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
    beat_bands : bool — add a "Beat Morphology" section with median and 5–95 %
                        bands of all R-peak-aligned beats (skipped when no beat
                        is detected in the real data).
    embedding_plots : list of go.Figure, optional — figures from
                        ``plot_embedding_2d`` shown in an "Embedding Projections"
                        section.
    gallery_selection : 'first' | 'random' — which recordings the ECG gallery
                        shows. 'random' draws them with ``gallery_seed``; the
                        chosen indices are printed under the gallery either way.
    gallery_seed : int

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
        real, synthetics, n_ecg_samples, leads, compare_mode, include_js,
        selection=gallery_selection, seed=gallery_seed, beat_bands=beat_bands,
    ))

    # 3b. Beat morphology bands (all detected beats, not hand-picked samples)
    if beat_bands:
        sections.append(_render_beat_bands(real, synthetics, leads))

    # 3c. Embedding projections
    if embedding_plots:
        sections.append(_render_embedding_section(embedding_plots))

    # 4. Metric sections
    for metric_name, by_synth in metric_results.items():
        sections.append(_render_metric_section(
            metric_name, by_synth, real.lead_names, include_js,
            fs=fs,
        ))

    # 5. Metrics summary table with CSV download
    if metric_results:
        sections.append(_render_summary_table(metric_results, synthetics))

    # 6. Radar summary (if multiple metrics)
    if len(metric_results) > 1:
        sections.append(_render_radar(metric_results, include_js))

    # 7. Clinical Feature Summary table
    if feature_df_real is not None and feature_dfs_synth:
        sections.append(_render_feature_summary_table(
            feature_df_real, feature_dfs_synth, synthetics
        ))

    # 8. 2D feature distribution plots
    if feature_plots_2d and feature_df_real is not None and feature_dfs_synth:
        for i, (sdf, sds) in enumerate(zip(feature_dfs_synth, synthetics)):
            sections.append(_render_feature_2d_section(
                feature_df_real, sdf, sds.label, include_js=(i == 0 and not metric_results)
            ))

    # 9. 3D feature distribution plots
    if feature_plots_3d and feature_df_real is not None and feature_dfs_synth:
        for i, (sdf, sds) in enumerate(zip(feature_dfs_synth, synthetics)):
            sections.append(_render_feature_3d_section(feature_df_real, sdf, sds.label))

    # 10. Citations
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
    selection: str = "first",
    seed: int = 42,
    beat_bands: bool = False,
) -> str:
    n_samples = min(n_samples, real.n_samples)
    more = " See Beat Morphology below for all beats." if beat_bands else ""
    indices = gallery_indices(real, synthetics, n_samples, selection, seed)
    plots_html = ""
    for k, i in enumerate(indices):
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
            include_plotlyjs=include_js if k == 0 else False,
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
  <p class="hint">
    Recordings shown: {"first" if selection == "first" else f"random (seed {seed})"}
    &nbsp;|&nbsp; indices {", ".join(str(i) for i in indices)}.
    A few samples cannot represent a dataset.{more}
  </p>
  {plots_html}
</div>
"""


def gallery_indices(
    real: ECGDataset,
    synthetics: List[ECGDataset],
    n_samples: int,
    selection: str = "first",
    seed: int = 42,
) -> List[int]:
    """Recording indices shown in the ECG gallery ('first' or seeded 'random')."""
    if selection not in ("first", "random"):
        raise ValueError(f"Unknown gallery_selection {selection!r}. Choose 'first' or 'random'.")
    n_samples = min(n_samples, real.n_samples)
    if selection == "first":
        return list(range(n_samples))
    pool = min([real.n_samples] + [s.n_samples for s in synthetics])
    n_samples = min(n_samples, pool)
    rng = np.random.default_rng(seed)
    return sorted(int(i) for i in rng.choice(pool, size=n_samples, replace=False))


def _render_beat_bands(
    real: ECGDataset,
    synthetics: List[ECGDataset],
    leads: Optional[List[str]],
) -> str:
    """Median and 5–95 % bands of R-peak-aligned beats; empty string if none are found."""
    try:
        fig = plot_beat_bands(real, synthetics, leads=leads)
    except Exception:  # a plot must never break the report
        return ""
    if not fig.data:
        return ""
    plot_html = fig.to_html(
        full_html=False, include_plotlyjs=False, config={"responsive": True},
    )
    return f"""
<div class="section">
  <h2>Beat Morphology</h2>
  <p class="hint">
    Every detected beat of each dataset, aligned at its R peak. Line: median beat.
    Shaded band: 5th to 95th percentile. The legend gives the number of beats used;
    a low count for a synthetic dataset means R-peak detection struggled on it.
  </p>
  {plot_html}
</div>
"""


def _render_embedding_section(figures: List[go.Figure]) -> str:
    plots_html = "".join(
        fig.to_html(full_html=False, include_plotlyjs=False, config={"responsive": True})
        for fig in figures
    )
    return f"""
<div class="section">
  <h2>Embedding Projections</h2>
  <p class="hint">
    Each point is one recording. Blue contours show where the real data lies.
    Qualitative only: distances and cluster sizes in t-SNE / UMAP plots are not
    quantitative, and overlap in 2-D does not prove that the distributions match.
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

    # Score table, with scalar extras that help to read the score
    extra_cols = [
        (key, title) for key, title in _EXTRA_COLUMNS
        if any(_is_number(r.extra.get(key)) for r in by_synth.values())
    ]
    score_rows = ""
    for label, result in by_synth.items():
        cells = "".join(
            f"<td>{result.extra[key]:.6f}</td>" if _is_number(result.extra.get(key))
            else "<td>—</td>"
            for key, _ in extra_cols
        )
        score_rows += (
            f"<tr><td>{label}</td><td><strong>{result.score:.6f}</strong></td>{cells}</tr>"
        )
    extra_head = "".join(f"<th>{title}</th>" for _, title in extra_cols)

    pairing_hint = ""
    if "pairing" in sample.extra:
        pairing_hint = (
            f' Pairing: <code>{sample.extra["pairing"]}</code> '
            f'({_PAIRING_TEXT.get(sample.extra["pairing"], "")}).'
        )

    table = f"""
  <table class="metric-table">
    <thead><tr><th>Dataset</th><th>Score</th>{extra_head}</tr></thead>
    <tbody>{score_rows}</tbody>
  </table>
  <p class="hint">{"Higher is better." if sample.higher_is_better else "Lower is better (0 = identical distributions)."}{pairing_hint}</p>
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

    # Amplitude histogram overlay (js_div metric)
    if metric_name.lower() == "js_div":
        hist_fig = plot_amplitude_hist(by_synth)
        if hist_fig.data:
            psd_html = hist_fig.to_html(
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


#: Scalar ``extra`` values shown as additional columns of a metric's score table.
_EXTRA_COLUMNS = [
    ("real_vs_real", "Real vs real (baseline)"),
    ("accuracy", "Classifier accuracy"),
    ("auc", "ROC AUC"),
    ("kl_real_synth", "KL(real ‖ synth)"),
    ("kl_synth_real", "KL(synth ‖ real)"),
    ("frac_rejected", "Share of tests rejected"),
]

_PAIRING_TEXT = {
    "nn": "each real signal vs its nearest synthetic signal",
    "paired": "real signal i vs synthetic signal i",
    "mean": "mean real waveform vs mean synthetic waveform",
}


def _is_number(value) -> bool:
    return isinstance(value, (int, float, np.floating)) and not isinstance(value, bool) \
        and bool(np.isfinite(value))


def _render_summary_table(
    metric_results: Dict[str, Dict[str, MetricResult]],
    synthetics: List[ECGDataset],
) -> str:
    """Render a combined metrics × datasets table with a CSV download button."""
    synth_labels = [s.label for s in synthetics]

    # Build header row
    header_cells = "<th>Metric</th><th>Direction</th>" + "".join(
        f"<th>{lbl}</th>" for lbl in synth_labels
    )

    # Build data rows and accumulate CSV lines
    csv_lines = ["metric,direction," + ",".join(synth_labels)]
    body_rows = ""
    for metric_name, by_synth in metric_results.items():
        sample = next(iter(by_synth.values()))
        direction = "↑ higher" if sample.higher_is_better else "↓ lower"
        direction_csv = "higher" if sample.higher_is_better else "lower"
        cells = f"<td><code>{metric_name}</code></td><td>{direction}</td>"
        csv_row = [metric_name, direction_csv]
        for lbl in synth_labels:
            if lbl in by_synth:
                val = by_synth[lbl].score
                cells += f"<td>{val:.6f}</td>"
                csv_row.append(f"{val:.6f}")
            else:
                cells += "<td>—</td>"
                csv_row.append("")
        body_rows += f"<tr>{cells}</tr>"
        csv_lines.append(",".join(csv_row))

    # Embed CSV as a JavaScript string and wire up the download button
    csv_content = "\\n".join(csv_lines).replace('"', '\\"')
    download_js = f"""
<script>
function downloadMetricsCSV() {{
  var csv = "{csv_content}";
  var blob = new Blob([csv], {{type: "text/csv"}});
  var url = URL.createObjectURL(blob);
  var a = document.createElement("a");
  a.href = url;
  a.download = "ecgen_eval_metrics.csv";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}}
</script>
"""

    return f"""
{download_js}
<div class="section">
  <h2>Metrics Summary</h2>
  <p class="hint">All metric scores in a single table. Click <strong>Download CSV</strong> to export.</p>
  <table class="summary-table">
    <thead><tr>{header_cells}</tr></thead>
    <tbody>{body_rows}</tbody>
  </table>
  <button class="download-btn" onclick="downloadMetricsCSV()">&#8595; Download CSV</button>
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


def _render_feature_summary_table(
    real_df,
    synth_dfs: list,
    synthetics: List[ECGDataset],
) -> str:
    """Render a Clinical Feature Summary table: mean ± std for real vs synthetic."""
    import pandas as pd
    import numpy as np

    # Numeric columns only, skip index/sample_idx
    exclude = {"sample_idx", "beat_idx", "lead", "r_sample"}
    cols = [c for c in real_df.columns if c not in exclude and pd.api.types.is_numeric_dtype(real_df[c])]

    if not cols:
        return ""

    from ecgen_eval.features.stats import compare_feature_distributions

    header = "<th>Feature</th>" + "<th>Real (mean ± std)</th>" + "".join(
        f"<th>{ds.label} (mean ± std)</th><th>{ds.label} KS D</th><th>{ds.label} p (Holm)</th>"
        for ds in synthetics
    )
    stats = []
    for sdf in synth_dfs:
        try:
            stats.append(compare_feature_distributions(real_df, sdf).set_index("feature"))
        except Exception:  # statistics are an add-on; never break the table
            stats.append(None)

    def _stat_cells(st, col) -> str:
        if st is None or col not in st.index or not np.isfinite(st.loc[col, "ks_D"]):
            return "<td>N/A</td><td>N/A</td>"
        p = st.loc[col, "ks_p_adjusted"]
        p_txt = "&lt;0.001" if p < 0.001 else f"{p:.3f}"
        return f"<td>{st.loc[col, 'ks_D']:.3f}</td><td>{p_txt}</td>"

    def _mean_std(series) -> str:
        vals = series.dropna()
        if vals.empty:
            return "N/A"
        return f"{vals.mean():.3f} ± {vals.std(ddof=0):.3f}"

    rows = ""
    for col in cols:
        cells = f"<td><code>{col}</code></td>"
        cells += f"<td>{_mean_std(real_df[col])}</td>"
        for sdf, st in zip(synth_dfs, stats):
            cells += f"<td>{_mean_std(sdf[col]) if col in sdf.columns else 'N/A'}</td>"
            cells += _stat_cells(st, col)
        rows += f"<tr>{cells}</tr>"

    return f"""
<div class="section">
  <h2>Clinical Feature Summary</h2>
  <p class="hint">Mean ± std of each feature across recordings. NaN indicates feature could not be extracted.
  KS D: two-sample Kolmogorov–Smirnov statistic against the real data (0 = same distribution, 1 = no overlap);
  p: its p-value, Holm-adjusted over the features. Read D as the effect size: p shrinks with sample size.</p>
  <table class="summary-table">
    <thead><tr>{header}</tr></thead>
    <tbody>{rows}</tbody>
  </table>
</div>
"""


def _render_feature_2d_section(real_df, synth_df, synth_label: str, include_js=False) -> str:
    """Render 2D feature distribution plots for one synthetic dataset."""
    fig = plot_feature_pair_grid(
        real_df, synth_df, synth_label=synth_label, real_label="Real"
    )
    plot_html = fig.to_html(
        full_html=False,
        include_plotlyjs=include_js,
        config={"responsive": True},
    )
    return f"""
<div class="section">
  <h2>Clinical Feature Distributions (2D) — {synth_label}</h2>
  <p class="hint">
    Scatter plots comparing real (blue) vs synthetic (orange) feature distributions.
    Each point represents one recording.
  </p>
  {plot_html}
</div>
"""


def _render_feature_3d_section(real_df, synth_df, synth_label: str) -> str:
    """Render 3D feature distribution plots for one synthetic dataset."""
    fig = plot_feature_triple_grid(
        real_df, synth_df, synth_label=synth_label, real_label="Real"
    )
    plot_html = fig.to_html(
        full_html=False,
        include_plotlyjs=False,
        config={"responsive": True},
    )
    return f"""
<div class="section">
  <h2>Clinical Feature Distributions (3D) — {synth_label}</h2>
  <p class="hint">
    Interactive 3D scatter: rotate by dragging. Real = blue, Synthetic = orange.
  </p>
  {plot_html}
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
    .download-btn {{
      display: inline-block;
      margin-top: 12px;
      padding: 8px 20px;
      background: #0f3460;
      color: #fff;
      border: none;
      border-radius: 6px;
      font-size: 0.9rem;
      font-weight: 600;
      cursor: pointer;
      text-decoration: none;
    }}
    .download-btn:hover {{ background: #16213e; }}
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
