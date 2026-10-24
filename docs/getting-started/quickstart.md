# Quick Start

This page walks through a complete evaluation in five minutes: create (or bring) data,
score it from the command line, then do the same from Python.

## 1. Prepare data

ECGEN-Eval works on arrays of shape `(N, L, T)`: **N** recordings × **L** leads ×
**T** timepoints. If your generator already writes `.npy` files in that shape, skip ahead.

To try things out, generate two toy datasets:

```python
import numpy as np

rng = np.random.default_rng(0)
real = rng.standard_normal((100, 12, 5000)).astype("float32")   # 100 × 12-lead × 10 s @ 500 Hz
synth = rng.standard_normal((100, 12, 5000)).astype("float32")

np.save("real_ecgs.npy", real)
np.save("synth_ecgs.npy", synth)
```

!!! note "Lead names"
    For 12-lead and 8-lead arrays, standard lead names (`I, II, III, aVR, aVL, aVF, V1–V6`
    or `I, II, V1–V6`) are assigned automatically. See [Loading Data](../user-guide/data-loading.md).

## 2. Run an evaluation from the CLI

```bash
ecgen-eval eval \
  --real real_ecgs.npy \
  --synthetic synth_ecgs.npy \
  -m mmd -m fd -m prd -m psd -m swd \
  --output report.html
```

Open `report.html` in a browser. It contains a dataset summary, an ECG gallery, one
section per metric and a radar chart summarising all scores.

!!! warning "Repeat `-m` for each metric"
    `--metrics` / `-m` is a repeatable option: write `-m mmd -m prd`, **not**
    `--metrics mmd prd`. If you omit it, *all* metrics run — including `fed`, which needs
    the `[fed]` extra and downloads model weights.

### Compare several models

Repeat `--synthetic` to put several models in one report:

```bash
ecgen-eval eval \
  --real real_ecgs.npy \
  --synthetic model_a.npy \
  --synthetic model_b.npy \
  --synth-labels "Model A,Model B" \
  -m mmd -m fd -m psd \
  --output comparison.html
```

### Add clinical feature plots

With the `[features]` extra installed:

```bash
ecgen-eval eval --real real_ecgs.npy --synthetic synth_ecgs.npy \
  -m mmd -m hrv -m heart_rate --feature-plots --output report.html
```

## 3. Use the Python API

```python
from ecgen_eval import load_ecg_npy, AVAILABLE_METRICS

real = load_ecg_npy("real_ecgs.npy", label="Real")
synth = load_ecg_npy("synth_ecgs.npy", label="Model A")
print(real)   # ECGDataset(label='Real', n_samples=100, leads=12, timepoints=5000, fs=500.0 Hz)

for key in ["mmd", "fd", "prd", "psnr"]:
    metric = AVAILABLE_METRICS[key]()
    result = metric.compute(real.data, synth.data, lead_names=real.lead_names)
    arrow = "↑" if result.higher_is_better else "↓"
    print(f"{key:>5} {arrow}  {result.score:.4f}")
```

Every metric returns a [`MetricResult`](../api/metrics.md#ecgen_eval.metrics.base.MetricResult)
with:

- `score` — the overall scalar score,
- `per_lead_scores` — `{lead_name: score}`,
- `extra` — metric-specific details (precision/recall, RMSE, PSD curves …),
- `higher_is_better` — how to read the score.

### Build a report from Python

```python
from ecgen_eval.report.html_report import generate_report

results = {}
for key in ["mmd", "psd", "dtw"]:
    m = AVAILABLE_METRICS[key]()
    results[key] = {synth.label: m.compute(real.data, synth.data, real.lead_names)}

generate_report(
    real=real,
    synthetics=[synth],
    metric_results=results,      # {metric_key: {synth_label: MetricResult}}
    output_path="report.html",
)
```

## Next steps

- Learn which metrics to trust for which question: [Metrics Overview](../user-guide/metrics.md)
- Use deep embeddings: [Fréchet ECG Distance](../user-guide/fed.md)
- Compare clinical intervals: [Clinical Features](../user-guide/features.md)
- All CLI options: [Command-Line Interface](../user-guide/cli.md)
