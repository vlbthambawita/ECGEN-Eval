"""
ecgen-eval CLI — entry point.

Commands
--------
  ecgen-eval eval         Run evaluation metrics and generate HTML report.
  ecgen-eval visualize    Generate ECG sample comparison plots only.
  ecgen-eval list-metrics List available metrics.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional, Tuple

import click

from ecgen_eval import __version__
from ecgen_eval.data.loader import load_ecg_folder
from ecgen_eval.metrics import AVAILABLE_METRICS
from ecgen_eval.report.html_report import generate_report


# ------------------------------------------------------------------ #
# CLI group                                                            #
# ------------------------------------------------------------------ #

@click.group()
@click.version_option(__version__, prog_name="ecgen-eval")
def main():
    """ECGEN-Eval: Evaluation metrics for synthetic ECG quality assessment."""
    pass


# ------------------------------------------------------------------ #
# eval command                                                         #
# ------------------------------------------------------------------ #

@main.command()
@click.option(
    "--real", "-r",
    required=True,
    type=click.Path(exists=True),
    help="Path to folder containing real ECG CSV files.",
)
@click.option(
    "--synthetic", "-s",
    multiple=True,
    required=True,
    type=click.Path(exists=True),
    help="Path to folder(s) containing synthetic ECG CSV files. Repeatable.",
)
@click.option(
    "--metrics", "-m",
    multiple=True,
    default=list(AVAILABLE_METRICS.keys()),
    show_default=True,
    type=click.Choice(list(AVAILABLE_METRICS.keys()), case_sensitive=False),
    help="Metrics to compute. Repeatable. Defaults to all available metrics.",
)
@click.option(
    "--output", "-o",
    default="ecgen_eval_report.html",
    show_default=True,
    help="Output HTML report path.",
)
@click.option(
    "--fs",
    default=500.0,
    show_default=True,
    help="Sampling frequency in Hz.",
)
@click.option(
    "--n-samples",
    default=3,
    show_default=True,
    help="Number of ECG samples to show in gallery.",
)
@click.option(
    "--leads",
    default=None,
    help="Comma-separated list of lead names to show (e.g. 'I,II,V1'). Default: all.",
)
@click.option(
    "--compare-mode",
    default="overlay",
    show_default=True,
    type=click.Choice(["overlay", "sidebyside", "grid"], case_sensitive=False),
    help="ECG comparison mode.",
)
@click.option(
    "--max-samples",
    default=None,
    type=int,
    help="Cap number of loaded recordings per folder (useful for quick tests).",
)
@click.option(
    "--offline",
    is_flag=True,
    default=False,
    help="Embed Plotly.js in HTML (larger file, no internet needed to view).",
)
@click.option(
    "--real-label",
    default=None,
    help="Display label for real dataset. Defaults to folder name.",
)
@click.option(
    "--synth-labels",
    default=None,
    help="Comma-separated labels for synthetic datasets. Defaults to folder names.",
)
@click.option(
    "--feature-plots",
    is_flag=True,
    default=False,
    help="Extract clinical features and add 2D/3D distribution plots to report.",
)
def eval(
    real,
    synthetic,
    metrics,
    output,
    fs,
    n_samples,
    leads,
    compare_mode,
    max_samples,
    offline,
    real_label,
    synth_labels,
    feature_plots,
):
    """Run evaluation metrics and generate an interactive HTML report."""

    click.echo(f"\n{'='*60}")
    click.echo(f"  ECGEN-Eval v{__version__}")
    click.echo(f"{'='*60}\n")

    # Parse optional labels
    synth_label_list = (
        [s.strip() for s in synth_labels.split(",")] if synth_labels else []
    )
    leads_list = [l.strip() for l in leads.split(",")] if leads else None

    # -------------------------------------------------------------- #
    # Load datasets                                                    #
    # -------------------------------------------------------------- #
    click.echo("Loading datasets...")
    real_ds = load_ecg_folder(
        real, fs=fs, label=real_label, max_samples=max_samples
    )
    click.echo(f"  Real:    {real_ds}")

    synth_datasets = []
    for i, s_path in enumerate(synthetic):
        lbl = synth_label_list[i] if i < len(synth_label_list) else None
        ds = load_ecg_folder(s_path, fs=fs, label=lbl, max_samples=max_samples)
        synth_datasets.append(ds)
        click.echo(f"  Synth {i+1}: {ds}")

    # -------------------------------------------------------------- #
    # Compute metrics                                                  #
    # -------------------------------------------------------------- #
    click.echo("\nComputing metrics...")
    metric_results: dict = {}

    for metric_key in metrics:
        metric_cls = AVAILABLE_METRICS[metric_key.lower()]
        metric_obj = metric_cls()
        click.echo(f"  [{metric_key.upper()}]")
        by_synth = {}
        for synth_ds in synth_datasets:
            click.echo(f"    Computing against {synth_ds.label} ...", nl=False)
            result = metric_obj.compute(
                real=real_ds.data,
                synth=synth_ds.data,
                lead_names=real_ds.lead_names,
            )
            by_synth[synth_ds.label] = result
            click.echo(f" score = {result.score:.6f}")
        metric_results[metric_key] = by_synth

    # -------------------------------------------------------------- #
    # Extract clinical features (optional)                             #
    # -------------------------------------------------------------- #
    feature_df_real = None
    feature_dfs_synth = None
    if feature_plots:
        click.echo("\nExtracting clinical features...")
        try:
            from ecgen_eval.features import extract_features

            _, feature_df_real = extract_features(real_ds)
            click.echo(f"  Real features: {feature_df_real.shape}")
            feature_dfs_synth = []
            for synth_ds in synth_datasets:
                _, sdf = extract_features(synth_ds)
                feature_dfs_synth.append(sdf)
                click.echo(f"  {synth_ds.label} features: {sdf.shape}")
        except Exception as exc:
            click.echo(f"  WARNING: Feature extraction failed ({exc}). Skipping feature plots.")
            feature_df_real = None
            feature_dfs_synth = None

    # -------------------------------------------------------------- #
    # Generate report                                                  #
    # -------------------------------------------------------------- #
    click.echo(f"\nGenerating report → {output}")
    out_path = generate_report(
        real=real_ds,
        synthetics=synth_datasets,
        metric_results=metric_results,
        output_path=output,
        n_ecg_samples=n_samples,
        leads=leads_list,
        compare_mode=compare_mode,
        plotly_cdn=not offline,
        feature_df_real=feature_df_real,
        feature_dfs_synth=feature_dfs_synth,
        feature_plots_2d=feature_plots,
        feature_plots_3d=feature_plots,
    )
    click.echo(f"\nDone!  Report saved to: {out_path.resolve()}")
    click.echo("Open in any modern browser.\n")


# ------------------------------------------------------------------ #
# visualize command                                                    #
# ------------------------------------------------------------------ #

@main.command()
@click.option("--real", "-r", required=True, type=click.Path(exists=True))
@click.option("--synthetic", "-s", multiple=True, required=True, type=click.Path(exists=True))
@click.option("--output", "-o", default="ecg_comparison.html", show_default=True)
@click.option("--fs", default=500.0, show_default=True)
@click.option("--n-samples", default=3, show_default=True)
@click.option("--leads", default=None, help="Comma-separated lead names.")
@click.option(
    "--compare-mode",
    default="overlay",
    type=click.Choice(["overlay", "sidebyside", "grid"]),
)
@click.option("--max-samples", default=None, type=int)
@click.option("--offline", is_flag=True, default=False)
def visualize(real, synthetic, output, fs, n_samples, leads, compare_mode, max_samples, offline):
    """Generate ECG sample comparison plots (no metrics)."""
    from ecgen_eval.visualization.ecg_waveform import plot_ecg_comparison

    leads_list = [l.strip() for l in leads.split(",")] if leads else None

    real_ds = load_ecg_folder(real, fs=fs, max_samples=max_samples)
    synth_datasets = [
        load_ecg_folder(s, fs=fs, max_samples=max_samples) for s in synthetic
    ]

    n_samples = min(n_samples, real_ds.n_samples)
    plots_html_parts = []
    include_js = "cdn" if not offline else True

    for i in range(n_samples):
        fig = plot_ecg_comparison(
            real=real_ds,
            synthetics=synth_datasets,
            sample_index=i,
            leads=leads_list,
            mode=compare_mode,
            add_calibration_pulse=True,
        )
        plots_html_parts.append(
            f"<h3>Sample {i}</h3>"
            + fig.to_html(
                full_html=False,
                include_plotlyjs=include_js if i == 0 else False,
                config={"responsive": True},
            )
        )

    cdn_tag = (
        '<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>'
        if not offline else ""
    )
    body = "\n".join(plots_html_parts)
    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"/>
<title>ECG Comparison</title>{cdn_tag}
<style>body{{font-family:sans-serif;max-width:1400px;margin:auto;padding:24px}}</style>
</head><body><h1>ECG Comparison ({compare_mode})</h1>{body}</body></html>"""

    Path(output).write_text(html, encoding="utf-8")
    click.echo(f"Saved: {Path(output).resolve()}")


# ------------------------------------------------------------------ #
# features command                                                     #
# ------------------------------------------------------------------ #

@main.command()
@click.option("--real", "-r", required=True, type=click.Path(exists=True),
              help="Path to folder containing real ECG files.")
@click.option("--synthetic", "-s", multiple=True, type=click.Path(exists=True),
              help="Path to folder(s) containing synthetic ECG files.")
@click.option("--output", "-o", default="ecg_features.csv", show_default=True,
              help="Output CSV path for the feature summary.")
@click.option("--fs", default=500.0, show_default=True, help="Sampling frequency in Hz.")
@click.option("--max-samples", default=None, type=int,
              help="Cap number of recordings per folder.")
@click.option("--lead", default="II", show_default=True,
              help="Lead to use for RR/interval detection.")
def features(real, synthetic, output, fs, max_samples, lead):
    """Extract clinical ECG features and save a summary CSV."""
    from ecgen_eval.features import extract_features

    click.echo(f"\n{'='*60}")
    click.echo(f"  ECGEN-Eval v{__version__} — Feature Extraction")
    click.echo(f"{'='*60}\n")

    real_ds = load_ecg_folder(real, fs=fs, max_samples=max_samples)
    click.echo(f"Loaded real: {real_ds}")

    _, real_feat_df = extract_features(real_ds, lead_for_intervals=lead)
    real_feat_df["dataset"] = real_ds.label

    dfs = [real_feat_df]

    for s_path in synthetic:
        sds = load_ecg_folder(s_path, fs=fs, max_samples=max_samples)
        click.echo(f"Loaded synthetic: {sds}")
        _, sdf = extract_features(sds, lead_for_intervals=lead)
        sdf["dataset"] = sds.label
        dfs.append(sdf)

    import pandas as pd
    combined = pd.concat(dfs, ignore_index=True)
    out = Path(output)
    combined.to_csv(out, index=False)
    click.echo(f"\nFeature summary saved to: {out.resolve()}")
    click.echo(f"Shape: {combined.shape[0]} rows × {combined.shape[1]} columns\n")


# ------------------------------------------------------------------ #
# list-metrics command                                                 #
# ------------------------------------------------------------------ #

@main.command(name="list-metrics")
def list_metrics():
    """List all available evaluation metrics."""
    click.echo(f"\nAvailable metrics in ecgen-eval v{__version__}:\n")
    for key, cls in AVAILABLE_METRICS.items():
        obj = cls()
        click.echo(f"  {key:<12} {obj.description[:80]}")
        click.echo(f"  {'':12} Ref: {obj.reference[:80]}...\n")


if __name__ == "__main__":
    main()
