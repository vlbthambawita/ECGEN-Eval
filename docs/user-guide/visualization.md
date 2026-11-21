# Visualization

All plots are interactive [Plotly](https://plotly.com/python/) figures. Call `fig.show()` in
a notebook, `fig.write_html("plot.html")` to save, or let
[`generate_report`](reports.md) embed them for you.

## ECG waveform comparison

[`plot_ecg_comparison`](../api/visualization.md#ecgen_eval.visualization.ecg_waveform.plot_ecg_comparison)
draws one recording from the real set and the recording at the same index from every
synthetic set on ECG graph paper (5 mm major / 1 mm minor grid), with an optional 1 mV
calibration pulse.

```python
from ecgen_eval.visualization import plot_ecg_comparison

fig = plot_ecg_comparison(
    real=real,
    synthetics=[synth_a, synth_b],
    sample_index=0,
    leads=["I", "II", "V1", "V5"],   # default: all leads
    mode="overlay",
    add_calibration_pulse=True,
)
fig.show()
```

| `mode` | Layout |
|---|---|
| `overlay` | One row per lead; real and synthetic traces drawn on top of each other |
| `sidebyside` | One row per lead, one column per dataset |
| `grid` | Compact rows = leads × columns = datasets view (currently the same layout as `sidebyside`) |

Synthetic recordings are not paired with real ones, so `sample_index` simply picks the
*i*-th recording of each set.

Pass `show_r_peaks=True` to mark the R peaks that ECGEN-Eval's detector finds on every trace
(open triangles). This shows what the rhythm metrics [`heart_rate`](../metrics/heart_rate.md)
and [`hrv`](../metrics/hrv.md) work with, and quickly reveals synthetic signals on which
detection fails.

## Beat morphology

Looking at a few recordings is the most common evaluation in the literature (62 papers in
the [Paper Database](../literature/database.md#metrics/Fidelity)) and the easiest to
cherry-pick. [`plot_beat_bands`](../api/visualization.md#ecgen_eval.visualization.beat_plots.plot_beat_bands)
summarises **every detected beat** of each dataset instead:

```python
from ecgen_eval.visualization import plot_beat_bands, extract_aligned_beats

# Median beat and 5–95 % band per dataset, one panel per lead
plot_beat_bands(real, [synth_a, synth_b], leads=["II", "V1", "V5"]).show()

# Time × amplitude density maps, one row per lead and one column per dataset
plot_beat_bands(real, [synth_a], mode="density", leads=["II"]).show()

# The aligned beats themselves: (n_beats, n_samples), R peak at a fixed index
beats = extract_aligned_beats(real, "II", pre_ms=250, post_ms=450)
```

How it works:

1. R peaks are detected once per recording on a reference lead (lead II if present, else the
   first lead) and reused for all leads, so the leads stay time-aligned.
2. A window from `pre_ms` before to `post_ms` after each R peak is cut out. Beats whose window
   crosses the edge of the recording are dropped.
3. `mode="bands"` draws the median beat and a shaded band between two quantiles
   (`quantiles=(0.05, 0.5, 0.95)` by default). `mode="density"` draws, for every time point,
   the share of beats at each amplitude.

| Parameter | Default | Description |
|---|---|---|
| `leads` | all | Leads to draw |
| `quantiles` | `(0.05, 0.5, 0.95)` | Lower band edge, centre line, upper band edge |
| `pre_ms`, `post_ms` | `250`, `450` | Window around the R peak |
| `mode` | `"bands"` | `"bands"` or `"density"` |
| `max_beats` | `5000` | Cap on beats per dataset (random subsample, fixed seed) |

What to look for:

- A synthetic **band narrower** than the real one means the model produces less variety than
  the data (mode collapse towards an average beat).
- A **shifted or missing** P or T wave in the median shows up directly.
- The legend gives the **number of beats** used per dataset. A low count for a synthetic
  dataset means R-peak detection struggled on it, which is itself a finding.

The plot is only as good as the R-peak detection. If no beat is found in the real dataset the
function returns a figure with a message instead of a plot.

### Graph-paper figures

[`make_ecg_paper_figure`](../api/visualization.md#ecgen_eval.visualization.ecg_paper.make_ecg_paper_figure)
returns an empty Plotly subplot grid styled as ECG paper, for building custom layouts:

```python
from ecgen_eval.visualization import make_ecg_paper_figure

fig = make_ecg_paper_figure(n_rows=3, n_cols=1, row_labels=["I", "II", "III"], fs=500)
```

## Metric plots

These functions take a mapping `{dataset_label: MetricResult}` for one metric.

```python
from ecgen_eval.visualization import (
    plot_per_lead_bar, plot_metric_violin, plot_psd_overlay, plot_amplitude_hist,
    plot_radar_chart,
)

mmd = AVAILABLE_METRICS["mmd"]()
res = {s.label: mmd.compute(real.data, s.data, real.lead_names) for s in [synth_a, synth_b]}
plot_per_lead_bar(res, metric_name="MMD").show()
```

| Function | Shows | Requires |
|---|---|---|
| `plot_per_lead_bar` | Grouped bar chart: leads × datasets | any per-lead metric |
| `plot_metric_violin` | Distribution of per-pair values per lead | `dtw` (`extra["per_lead_all_distances"]`) or a pairwise metric: `mse`, `rmse`, `euclidean`, `pearson`, `cosine`, `curve_frechet` (`extra["per_lead_all_values"]`) |
| `plot_psd_overlay` | Mean normalised PSD, real vs synthetic, per lead | `psd` results |
| `plot_amplitude_hist` | Amplitude-value histograms, real vs synthetic, per lead | `js_div` results |
| `plot_radar_chart` | One polygon per dataset across metrics, normalised so the outer edge is best | `{label: {metric: score}}` |

```python
scores = {
    "Model A": {"mmd": 0.01, "fd": 3.2, "psnr": 18.0},
    "Model B": {"mmd": 0.03, "fd": 5.1, "psnr": 15.5},
}
plot_radar_chart(scores, higher_is_better={"mmd": False, "fd": False, "psnr": True}).show()
```

## Embedding projections

Projecting real and synthetic recordings to two dimensions (PCA, t-SNE, UMAP) is used by 26
papers in the [Paper Database](../literature/database.md#metrics/Fidelity).
[`compute_embedding_2d`](../api/visualization.md#ecgen_eval.visualization.embedding_plots.compute_embedding_2d)
computes the projection and
[`plot_embedding_2d`](../api/visualization.md#ecgen_eval.visualization.embedding_plots.plot_embedding_2d)
draws it.

```python
from ecgen_eval.visualization import compute_embedding_2d, plot_embedding_2d

emb = compute_embedding_2d(real, [synth_a, synth_b], method="pca", features="handcrafted")
plot_embedding_2d(emb).show()

emb["real"]            # (N, 2) coordinates of the real recordings
emb["synth"]["Model A"]
emb["meta"]            # method, fit_on, n_per_set, axis labels, sample indices
```

| `method` | Fitted on | Needs | Notes |
|---|---|---|---|
| `"pca"` (default) | real data only | — | Linear and deterministic. The axis labels give the share of real variance explained. |
| `"umap"` | real data only | `pip install "ecgen-eval[umap]"` | Non-linear. Synthetic points are projected into the map of the real data. |
| `"tsne"` | real and synthetic jointly | — | t-SNE cannot project new points, so the fit is always joint. The figure title says so. |

| `features` | What is projected |
|---|---|
| `"handcrafted"` (default) | The 11 signal features of [`fd`](../metrics/fd.md) for every lead, standardised |
| `"signal"` | The waveform of all leads, decimated and reduced to 50 principal components first |
| `"clinical"` | Clinical features: pass the `summary_df` DataFrames of [`FeatureExtractor`](features.md) instead of datasets. Rows with a missing value are dropped (`meta["n_dropped"]`) |
| *(arrays)* | Any `(N, F)` arrays, for example embeddings of a foundation model |

Two defaults make the plot harder to misread:

- **The map is fitted on the real data only** (`fit_on="real"`), and synthetic recordings are
  projected into it. With a joint fit, the synthetic set changes the map it is judged on.
- **Real data is drawn as density contours**, with the synthetic points on top, and every set
  is cut to the same number of points (`n_subsample`, default 1000). Synthetic points outside
  the contours are off the real manifold; contours without synthetic points are regions the
  model does not cover.

!!! warning "Qualitative only"
    Distances, cluster sizes and gaps in t-SNE and UMAP plots are not quantitative, and they
    change with `perplexity` / `n_neighbors` and the seed. Overlap in two dimensions does not
    prove that two distributions match. Use the plot to find *where* to look, and
    [`fed`](../metrics/fed.md), [`mmd`](../metrics/mmd.md),
    [`pr_dist`](../metrics/pr_dist.md) or [`c2st`](../metrics/c2st.md) for a number.

## Clinical feature plots

Functions in `ecgen_eval.visualization.feature_plots` compare
[clinical feature](features.md) tables (`summary_df`) between real and synthetic data.
Rows with `NaN` in the plotted columns are dropped.

```python
from ecgen_eval.visualization.feature_plots import (
    plot_feature_2d, plot_feature_pair_grid, plot_feature_2d_multi,
    plot_feature_3d, plot_feature_triple_grid,
)

# Scatter + 2D density contours for one pair
plot_feature_2d(summ_real, summ_synth, "rr_mean_ms", "hr_bpm", synth_label="ECGEN-FM").show()

# Grid of the default pairs
plot_feature_pair_grid(summ_real, summ_synth).show()

# Several synthetic models in one 2D plot
plot_feature_2d_multi(summ_real, [summ_a, summ_b], "qrs_duration_ms", "qt_interval_ms",
                      synth_labels=["A", "B"]).show()

# Interactive, rotatable 3D scatter
plot_feature_3d(summ_real, summ_synth, "rr_mean_ms", "hr_bpm", "qrs_duration_ms").show()

# Grid of the default triples
plot_feature_triple_grid(summ_real, summ_synth).show()
```

Default pairs and triples (filtered to available columns):

=== "DEFAULT_2D_PAIRS"

    | x | y |
    |---|---|
    | `rr_mean_ms` | `hr_bpm` |
    | `qrs_duration_ms` | `qt_interval_ms` |
    | `st_deviation_mv` | `t_amplitude_mv` |
    | `rr_mean_ms` | `hrv_sdnn_ms` |

=== "DEFAULT_3D_TRIPLES"

    | x | y | z |
    |---|---|---|
    | `rr_mean_ms` | `hr_bpm` | `qrs_duration_ms` |
    | `pr_interval_ms` | `qt_interval_ms` | `hrv_sdnn_ms` |
    | `st_deviation_mv` | `t_amplitude_mv` | `qrs_duration_ms` |

Pass your own lists via `pairs=` / `triples=`.
