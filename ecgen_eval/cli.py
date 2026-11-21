"""
ecgen-eval CLI — entry point.

Commands
--------
  ecgen-eval eval         Run evaluation metrics and generate HTML report.
  ecgen-eval visualize    Generate ECG sample comparison plots only.
  ecgen-eval list-metrics List available metrics.
"""

from __future__ import annotations

import inspect
import sys
from pathlib import Path
from typing import List, Optional, Tuple

import click

from ecgen_eval import __version__
from ecgen_eval.data.loader import load_ecg_folder
from ecgen_eval.metrics import AVAILABLE_METRICS
from ecgen_eval.report.html_report import generate_report

# Curated default: one or two metrics per evaluation question, without near-duplicates
# (mse / euclidean / mae / prd / psnr repeat rmse; swd / ks_test share mmd's features) and
# without the metrics that separate generators poorly (cosine, curve_frechet).
DEFAULT_METRICS = [
    "fd", "mmd", "pr_dist", "c2st",        # distribution
    "rmse", "pearson", "dtw",              # waveform: amplitude error, shape, shape with warping
    "js_div",                              # amplitude values
    "psd",                                 # frequency content
    "heart_rate", "hrv",                   # rhythm
    "nn_dist",                             # memorisation
]

# `-m all` runs every registered metric except `fed`, which needs the [fed] extras and downloads
# model weights, so it must always be requested explicitly (`-m all -m fed`).
ALL_METRICS = [k for k in AVAILABLE_METRICS if k != "fed"]


def resolve_metrics(selected) -> List[str]:
    """Expand ``all`` and drop duplicates, keeping the order in which metrics were requested."""
    out: List[str] = []
    for key in selected:
        key = key.lower()
        for k in (ALL_METRICS if key == "all" else [key]):
            if k not in out:
                out.append(k)
    return out


# ------------------------------------------------------------------ #
# CLI group                                                            #
# ------------------------------------------------------------------ #

@click.group()
@click.version_option(__version__, prog_name="ecgen-eval")
def main():
    """ECGEN-Eval: Evaluation metrics for synthetic ECG quality assessment."""
    pass



# ------------------------------------------------------------------ #
# Shared feature-extraction options                                    #
# ------------------------------------------------------------------ #

def _feature_options(func):
    """Options choosing which clinical features to compute and with which library."""
    from ecgen_eval.features.backends import AVAILABLE_BACKENDS, DEFAULT_BACKEND

    delineation_methods = sorted({m for cls in AVAILABLE_BACKENDS.values()
                                  for m in cls.delineation_methods})
    options = [
        click.option("--feature", "-F", "feature_select", multiple=True,
                     help="Feature group (rhythm, intervals, amplitude, hrv) or column "
                          "(e.g. qtc_bazett_ms) to extract. Repeatable. Default: all. "
                          "See `ecgen-eval list-features`."),
        click.option("--feature-backend", default=DEFAULT_BACKEND, show_default=True,
                     type=click.Choice(sorted(AVAILABLE_BACKENDS), case_sensitive=False),
                     help="Library that detects beats and delineates P/QRS/T waves."),
        click.option("--rpeak-method", default=None,
                     help="R-peak detector of the chosen backend (hybrid / neurokit2: a "
                          "neurokit2 ecg_peaks method or 'scipy'; biosppy: hamilton, christov, "
                          "...). Default: backend's own. See `ecgen-eval list-features`."),
        click.option("--delineation-method", default=None,
                     type=click.Choice(delineation_methods),
                     help="P/QRS/T delineation method, for backends that offer a choice "
                          "(hybrid default: prominence, neurokit2 default: dwt)."),
    ]
    for option in reversed(options):
        func = option(func)
    return func


def _build_extractor(feature_select, feature_backend, rpeak_method, delineation_method,
                     lead="II"):
    from ecgen_eval.features import FeatureExtractor, get_backend

    kwargs = {}
    if rpeak_method is not None:
        kwargs["rpeak_method"] = rpeak_method
    if delineation_method is not None:
        kwargs["method"] = delineation_method
    try:
        backend = get_backend(feature_backend, **kwargs)
    except ValueError as exc:
        hint = "--delineation-method" if "delineation" in str(exc) else "--rpeak-method"
        raise click.BadParameter(str(exc), param_hint=hint) from exc
    try:
        return FeatureExtractor(
            lead_for_intervals=lead,
            features=list(feature_select) or None,
            backend=backend,
        )
    except ValueError as exc:
        raise click.BadParameter(str(exc), param_hint="--feature") from exc


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
    default=DEFAULT_METRICS,
    show_default=True,
    type=click.Choice(list(AVAILABLE_METRICS.keys()) + ["all"], case_sensitive=False),
    help="Metric to compute. Repeatable (-m mmd -m prd). 'all' runs every metric except 'fed' "
         "(add -m fed to include it). Defaults to a curated set of 12 metrics.",
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
@_feature_options
@click.option(
    "--pairing",
    default="nn",
    show_default=True,
    type=click.Choice(["nn", "paired", "mean"], case_sensitive=False),
    help="How waveform metrics (mse, rmse, pearson, cosine, euclidean, curve_frechet) match "
         "real and synthetic signals: nearest neighbour, index-aligned pairs (needs equal "
         "counts), or mean waveforms.",
)
@click.option(
    "--beat-bands/--no-beat-bands",
    default=True,
    show_default=True,
    help="Add the Beat Morphology section (median and 5-95 % bands of all detected beats).",
)
@click.option(
    "--embedding-plots",
    is_flag=True,
    default=False,
    help="Add 2-D embedding projections of real vs synthetic recordings to the report.",
)
@click.option(
    "--embedding-method",
    multiple=True,
    default=("pca",),
    show_default=True,
    type=click.Choice(["pca", "tsne", "umap"], case_sensitive=False),
    help="Projection for --embedding-plots. Repeatable. 'umap' needs the [umap] extra.",
)
@click.option(
    "--embedding-features",
    default="handcrafted",
    show_default=True,
    type=click.Choice(["handcrafted", "signal", "clinical"], case_sensitive=False),
    help="What is projected: 11 signal features per lead, the raw waveform, or the "
         "clinical features (the latter runs feature extraction).",
)
@click.option(
    "--gallery-selection",
    default="first",
    show_default=True,
    type=click.Choice(["first", "random"], case_sensitive=False),
    help="Recordings shown in the ECG gallery: the first ones or a seeded random draw.",
)
@click.option(
    "--backbone",
    default="ecgfounder",
    show_default=True,
    type=click.Choice(["ecgfounder", "hubert_ecg", "ecgfm"], case_sensitive=False),
    help="Foundation model backbone to use when 'fed' metric is selected.",
)
@click.option(
    "--fed-device",
    default="cpu",
    show_default=True,
    help="PyTorch device for FED encoder (e.g. 'cpu' or 'cuda').",
)
@click.option(
    "--fed-batch-size",
    default=32,
    show_default=True,
    type=int,
    help="Batch size for FED encoder forward passes.",
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
    feature_select,
    feature_backend,
    rpeak_method,
    delineation_method,
    pairing,
    beat_bands,
    embedding_plots,
    embedding_method,
    embedding_features,
    gallery_selection,
    backbone,
    fed_device,
    fed_batch_size,
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
    need_features = feature_plots or (embedding_plots and embedding_features == "clinical")
    extractor = (
        _build_extractor(feature_select, feature_backend, rpeak_method, delineation_method)
        if need_features else None
    )

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
        if ds.fs != real_ds.fs:
            click.echo(
                f"  WARNING: {ds.label} is sampled at {ds.fs} Hz but the real data at "
                f"{real_ds.fs} Hz. Resample for meaningful comparisons."
            )

    # -------------------------------------------------------------- #
    # Compute metrics                                                  #
    # -------------------------------------------------------------- #
    if pairing == "paired":
        for ds in synth_datasets:
            if ds.n_samples != real_ds.n_samples:
                raise click.UsageError(
                    f"--pairing paired needs the same number of recordings in every dataset: "
                    f"{real_ds.label} has {real_ds.n_samples}, {ds.label} has {ds.n_samples}."
                )

    metrics = resolve_metrics(metrics)
    click.echo("\nComputing metrics...")
    metric_results: dict = {}

    for metric_key in metrics:
        metric_cls = AVAILABLE_METRICS[metric_key.lower()]
        if metric_key.lower() == "fed":
            metric_obj = metric_cls(
                backbone=backbone,
                device=fed_device,
                batch_size=fed_batch_size,
            )
        else:
            params = inspect.signature(metric_cls.__init__).parameters
            kwargs = {}
            if "fs" in params:
                kwargs["fs"] = real_ds.fs
            if "pairing" in params:
                kwargs["pairing"] = pairing
            metric_obj = metric_cls(**kwargs)
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
    if need_features:
        click.echo(f"\nExtracting clinical features ({extractor.backend!r})...")
        try:
            _, feature_df_real = extractor.extract(real_ds)
            click.echo(f"  Real features: {feature_df_real.shape}")
            feature_dfs_synth = []
            for synth_ds in synth_datasets:
                _, sdf = extractor.extract(synth_ds)
                feature_dfs_synth.append(sdf)
                click.echo(f"  {synth_ds.label} features: {sdf.shape}")
        except Exception as exc:
            click.echo(f"  WARNING: Feature extraction failed ({exc}). Skipping feature plots.")
            feature_df_real = None
            feature_dfs_synth = None

    # -------------------------------------------------------------- #
    # Embedding projections (optional)                                 #
    # -------------------------------------------------------------- #
    embedding_figs = []
    if embedding_plots:
        from ecgen_eval.visualization.embedding_plots import (
            compute_embedding_2d,
            plot_embedding_2d,
        )

        click.echo("\nComputing embedding projections...")
        if embedding_features == "clinical":
            emb_real = feature_df_real
            emb_synth = (
                {ds.label: df for ds, df in zip(synth_datasets, feature_dfs_synth)}
                if feature_dfs_synth else None
            )
        else:
            emb_real, emb_synth = real_ds, synth_datasets
        for method in embedding_method:
            if emb_real is None or emb_synth is None:
                click.echo("  WARNING: clinical features unavailable. Skipping embedding plots.")
                break
            try:
                emb = compute_embedding_2d(
                    emb_real, emb_synth, method=method, features=embedding_features
                )
                emb["meta"]["real_label"] = real_ds.label
                embedding_figs.append(plot_embedding_2d(emb))
                click.echo(f"  {method}: {emb['meta']['n_per_set']} points per set")
            except (ImportError, ValueError) as exc:
                click.echo(f"  WARNING: {method} projection skipped ({exc})")

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
        fs=real_ds.fs,
        feature_df_real=feature_df_real,
        feature_dfs_synth=feature_dfs_synth,
        feature_plots_2d=feature_plots,
        feature_plots_3d=feature_plots,
        beat_bands=beat_bands,
        embedding_plots=embedding_figs,
        gallery_selection=gallery_selection,
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
    type=click.Choice(["overlay", "sidebyside", "grid", "beats", "beat-density"]),
    help="overlay / sidebyside / grid show individual recordings; beats shows median and "
         "5-95 % bands of all R-peak-aligned beats; beat-density shows their density maps.",
)
@click.option("--max-samples", default=None, type=int)
@click.option("--offline", is_flag=True, default=False)
@click.option("--show-r-peaks", is_flag=True, default=False,
              help="Mark detected R peaks on every trace.")
@click.option("--embedding", "embedding", multiple=True,
              type=click.Choice(["pca", "tsne", "umap"], case_sensitive=False),
              help="Also add a 2-D embedding projection (11 signal features per lead). "
                   "Repeatable.")
def visualize(real, synthetic, output, fs, n_samples, leads, compare_mode, max_samples, offline,
              show_r_peaks, embedding):
    """Generate ECG sample comparison plots (no metrics)."""
    from ecgen_eval.visualization.beat_plots import plot_beat_bands
    from ecgen_eval.visualization.ecg_waveform import plot_ecg_comparison

    leads_list = [l.strip() for l in leads.split(",")] if leads else None

    real_ds = load_ecg_folder(real, fs=fs, max_samples=max_samples)
    synth_datasets = [
        load_ecg_folder(s, fs=fs, max_samples=max_samples) for s in synthetic
    ]

    n_samples = min(n_samples, real_ds.n_samples)
    plots_html_parts = []
    include_js = "cdn" if not offline else True

    if compare_mode in ("beats", "beat-density"):
        fig = plot_beat_bands(
            real_ds, synth_datasets, leads=leads_list,
            mode="bands" if compare_mode == "beats" else "density",
        )
        plots_html_parts.append(
            fig.to_html(full_html=False, include_plotlyjs=include_js,
                        config={"responsive": True})
        )
        n_samples = 0

    for i in range(n_samples):
        fig = plot_ecg_comparison(
            real=real_ds,
            synthetics=synth_datasets,
            sample_index=i,
            leads=leads_list,
            mode=compare_mode,
            add_calibration_pulse=True,
            show_r_peaks=show_r_peaks,
        )
        plots_html_parts.append(
            f"<h3>Sample {i}</h3>"
            + fig.to_html(
                full_html=False,
                include_plotlyjs=include_js if i == 0 else False,
                config={"responsive": True},
            )
        )

    if embedding:
        from ecgen_eval.visualization.embedding_plots import (
            compute_embedding_2d,
            plot_embedding_2d,
        )

        for method in embedding:
            try:
                fig = plot_embedding_2d(
                    compute_embedding_2d(real_ds, synth_datasets, method=method)
                )
            except (ImportError, ValueError) as exc:
                click.echo(f"WARNING: {method} projection skipped ({exc})")
                continue
            plots_html_parts.append(
                f"<h3>{method.upper()} projection</h3>"
                + fig.to_html(
                    full_html=False,
                    include_plotlyjs=include_js if not plots_html_parts else False,
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
@click.option("--stats-output", default=None,
              help="Also write a CSV of two-sample tests (KS, Mann-Whitney, Cohen's d) between "
                   "the real and each synthetic feature distribution.")
@_feature_options
def features(real, synthetic, output, fs, max_samples, lead, stats_output, feature_select,
             feature_backend, rpeak_method, delineation_method):
    """Extract clinical ECG features and save a summary CSV."""
    extractor = _build_extractor(feature_select, feature_backend, rpeak_method,
                                 delineation_method, lead=lead)

    click.echo(f"\n{'='*60}")
    click.echo(f"  ECGEN-Eval v{__version__} — Feature Extraction")
    click.echo(f"{'='*60}\n")
    click.echo(f"Extractor: {extractor!r}\n")

    real_ds = load_ecg_folder(real, fs=fs, max_samples=max_samples)
    click.echo(f"Loaded real: {real_ds}")

    _, real_feat_df = extractor.extract(real_ds)
    real_feat_df["dataset"] = real_ds.label

    dfs = [real_feat_df]
    stats = []

    for s_path in synthetic:
        sds = load_ecg_folder(s_path, fs=fs, max_samples=max_samples)
        click.echo(f"Loaded synthetic: {sds}")
        _, sdf = extractor.extract(sds)
        if stats_output:
            from ecgen_eval.features import compare_feature_distributions

            st = compare_feature_distributions(real_feat_df, sdf)
            st.insert(0, "dataset", sds.label)
            stats.append(st)
        sdf["dataset"] = sds.label
        dfs.append(sdf)

    import pandas as pd
    combined = pd.concat(dfs, ignore_index=True)
    out = Path(output)
    combined.to_csv(out, index=False)
    click.echo(f"\nFeature summary saved to: {out.resolve()}")
    click.echo(f"Shape: {combined.shape[0]} rows × {combined.shape[1]} columns\n")
    if stats_output:
        if stats:
            stats_path = Path(stats_output)
            pd.concat(stats, ignore_index=True).to_csv(stats_path, index=False)
            click.echo(f"Feature statistics saved to: {stats_path.resolve()}\n")
        else:
            click.echo("--stats-output needs at least one --synthetic dataset; nothing written.\n")


# ------------------------------------------------------------------ #
# list-metrics command                                                 #
# ------------------------------------------------------------------ #

@main.command(name="list-metrics")
def list_metrics():
    """List all available evaluation metrics."""
    click.echo(f"\nAvailable metrics in ecgen-eval v{__version__}:\n")
    for key, cls in AVAILABLE_METRICS.items():
        obj = cls()
        click.echo(f"  {key:<17} {obj.description[:80]}")
        click.echo(f"  {'':17} Ref: {obj.reference[:80]}...\n")



@main.command(name="list-features")
def list_features():
    """List the clinical feature groups and extraction backends."""
    from ecgen_eval.features import AVAILABLE_BACKENDS, AVAILABLE_FEATURE_GROUPS

    click.echo("\nFeature groups (select with --feature <group> or --feature <column>):\n")
    for name, group in AVAILABLE_FEATURE_GROUPS.items():
        click.echo(f"  {name:<12} {group.description}")
        click.echo(f"  {'':12} columns: {', '.join(group.columns)}\n")
    click.echo("Backends (select with --feature-backend):\n")
    for name, cls in AVAILABLE_BACKENDS.items():
        status = "" if cls.is_available() else "  [not installed]"
        click.echo(f"  {name:<12} {cls.description}{status}")
        click.echo(f"  {'':12} requires: {', '.join(cls.requires) or '-'}")
        if cls.rpeak_methods:
            click.echo(f"  {'':12} --rpeak-method: {', '.join(cls.rpeak_methods)}")
        if cls.delineation_methods:
            click.echo(f"  {'':12} --delineation-method: {', '.join(cls.delineation_methods)}")
        click.echo("")


if __name__ == "__main__":
    main()
