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
    plot_per_lead_bar, plot_metric_violin, plot_psd_overlay, plot_radar_chart,
)

mmd = AVAILABLE_METRICS["mmd"]()
res = {s.label: mmd.compute(real.data, s.data, real.lead_names) for s in [synth_a, synth_b]}
plot_per_lead_bar(res, metric_name="MMD").show()
```

| Function | Shows | Requires |
|---|---|---|
| `plot_per_lead_bar` | Grouped bar chart: leads × datasets | any per-lead metric |
| `plot_metric_violin` | Distribution of pairwise distances per lead | `dtw` (`extra["per_lead_all_distances"]`) |
| `plot_psd_overlay` | Mean normalised PSD, real vs synthetic, per lead | `psd` results |
| `plot_radar_chart` | One polygon per dataset across metrics, normalised so the outer edge is best | `{label: {metric: score}}` |

```python
scores = {
    "Model A": {"mmd": 0.01, "fd": 3.2, "psnr": 18.0},
    "Model B": {"mmd": 0.03, "fd": 5.1, "psnr": 15.5},
}
plot_radar_chart(scores, higher_is_better={"mmd": False, "fd": False, "psnr": True}).show()
```

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
