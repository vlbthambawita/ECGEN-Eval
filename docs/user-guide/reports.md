# HTML Reports

[`generate_report`](../api/report.md) writes a **single, self-contained HTML file** with every
figure embedded. It is what `ecgen-eval eval` produces, and it can be opened in any modern
browser or shared as one file.

## Contents

| Section | Description |
|---|---|
| Dataset summary | Recordings, leads, length and sampling rate for each dataset |
| ECG gallery | Real vs synthetic recordings on ECG graph paper (`overlay` / `sidebyside` / `grid`). The indices of the recordings shown are printed below it |
| Beat morphology | Median and 5–95 % band of all R-peak-aligned beats per dataset and lead; see [Beat morphology](visualization.md#beat-morphology). Skipped when no beat is detected |
| Embedding projections *(optional)* | PCA / t-SNE / UMAP plots of real vs synthetic recordings; see [Embedding projections](visualization.md#embedding-projections) |
| Per-metric sections | Score table, per-lead bar chart, plus a PSD overlay for `psd`, an amplitude-histogram overlay for `js_div`, and a violin plot for `dtw` and the pairwise metrics. The score table adds the real-vs-real baseline, classifier accuracy and AUC, or KL values where a metric provides them, and names the `pairing` |
| Radar chart | All metrics and datasets at a glance, normalised so that the outer edge is best |
| Metrics summary table | All scores in one table, with a **Download CSV** button |
| Clinical feature summary *(optional)* | Mean ± std per feature, real vs synthetic, with the two-sample KS statistic and its Holm-adjusted p-value for every synthetic dataset |
| 2D / 3D feature plots *(optional)* | Distribution plots of [clinical features](features.md) |
| References | Citation for every metric used |

## From the CLI

```bash
ecgen-eval eval --real real.npy --synthetic a.npy --synthetic b.npy \
  -m mmd -m fd -m psd -m dtw --feature-plots --output report.html
```

See [Command-Line Interface](cli.md) for all options.

## From Python

```python
from ecgen_eval import load_ecg_npy, AVAILABLE_METRICS
from ecgen_eval.features import extract_features
from ecgen_eval.report.html_report import generate_report

real = load_ecg_npy("real.npy", label="PTB-XL")
synths = [load_ecg_npy("a.npy", label="Model A"), load_ecg_npy("b.npy", label="Model B")]

metric_results = {}
for key in ["mmd", "fd", "psd", "dtw", "pr_dist"]:
    metric = AVAILABLE_METRICS[key]()
    metric_results[key] = {
        s.label: metric.compute(real.data, s.data, lead_names=real.lead_names) for s in synths
    }

_, feat_real = extract_features(real)
feat_synth = [extract_features(s)[1] for s in synths]

generate_report(
    real=real,
    synthetics=synths,
    metric_results=metric_results,
    output_path="report.html",
    n_ecg_samples=5,
    leads=["I", "II", "V1", "V5"],
    compare_mode="sidebyside",
    plotly_cdn=True,
    feature_df_real=feat_real,
    feature_dfs_synth=feat_synth,
    feature_plots_2d=True,
    feature_plots_3d=True,
)
```

Embedding projections are passed in as ready-made figures:

```python
from ecgen_eval.visualization import compute_embedding_2d, plot_embedding_2d

figs = [plot_embedding_2d(compute_embedding_2d(real, synths, method=m)) for m in ("pca", "tsne")]
generate_report(real, synths, metric_results, "report.html",
                embedding_plots=figs, gallery_selection="random")
```

### Parameters

| Parameter | Default | Description |
|---|---|---|
| `real` | — | Real `ECGDataset` |
| `synthetics` | — | List of synthetic `ECGDataset`s |
| `metric_results` | — | `{metric_key: {synth_label: MetricResult}}` |
| `output_path` | — | Path of the HTML file to write |
| `n_ecg_samples` | `3` | Recordings shown in the gallery |
| `leads` | `None` | Subset of leads shown in the gallery (all if `None`) |
| `compare_mode` | `"overlay"` | `overlay`, `sidebyside` or `grid` |
| `plotly_cdn` | `True` | Load Plotly.js from a CDN (small file). `False` embeds it (~3–4 MB larger, works offline) |
| `fs` | `500.0` | Sampling rate used for PSD frequency axes |
| `feature_df_real` | `None` | Real `summary_df` from feature extraction |
| `feature_dfs_synth` | `None` | List of synthetic `summary_df`s, same order as `synthetics` |
| `feature_plots_2d` | `False` | Add 2D feature distribution plots |
| `feature_plots_3d` | `False` | Add 3D feature distribution plots |
| `beat_bands` | `True` | Add the Beat morphology section |
| `embedding_plots` | `None` | List of figures from `plot_embedding_2d` for the Embedding projections section |
| `gallery_selection` | `"first"` | Recordings shown in the gallery: `"first"` or `"random"` (seeded with `gallery_seed`) |
| `gallery_seed` | `42` | Seed for `gallery_selection="random"` |

Returns the `Path` of the written file.

!!! tip "Offline viewing"
    Reports load Plotly.js from a CDN by default. Use `plotly_cdn=False` (`--offline` on the
    CLI) when the report will be opened without internet access, e.g. on a secure cluster.
