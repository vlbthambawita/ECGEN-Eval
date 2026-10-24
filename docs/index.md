# ECGEN-Eval

[:material-tag: v{{ ecgen_version }}](changelog.md){ .md-button } [:material-github: Source](https://github.com/vlbthambawita/ECGEN-Eval){ .md-button }

**Evaluation metrics and interactive HTML reports for synthetic ECG quality assessment.**

ECGEN-Eval answers one question: *how close are the ECGs produced by a generative model to
real ECGs?* It loads real and synthetic recordings from common formats, scores them with
16 complementary metrics, extracts clinically meaningful features, and bundles everything
into a single self-contained, interactive HTML report.

It is part of the ECGEN research suite alongside ECGEN-FM, ECGEN-VAE, ECGEN Pulse2Pulse+
and Pulse2Pulse, but it works with output from any ECG generator.

<div class="grid cards" markdown>

-   :material-download: **Install in a minute**

    ---

    `pip install -e .` and optional extras for clinical features and foundation-model metrics.

    [:octicons-arrow-right-24: Installation](getting-started/installation.md)

-   :material-rocket-launch: **Evaluate a model**

    ---

    One CLI call produces a full interactive report comparing real and synthetic ECGs.

    [:octicons-arrow-right-24: Quick Start](getting-started/quickstart.md)

-   :material-chart-bell-curve: **16 metrics**

    ---

    Distribution distances, signal fidelity, spectral, physiological, privacy and
    foundation-model (FED) metrics.

    [:octicons-arrow-right-24: Metrics Overview](user-guide/metrics.md)

-   :material-heart-pulse: **Clinical features**

    ---

    RR, HR, PR, QRS, QT, QTc, ST, T-wave, P-wave and HRV, with 2D/3D distribution plots.

    [:octicons-arrow-right-24: Clinical Features](user-guide/features.md)

</div>

## Highlights

- **Multi-format loading** — NumPy (`.npy` / `.npz`), WFDB (PTB-XL, PhysioNet) and three CSV
  layouts, all normalised to a single `(N, L, T)` array (recordings × leads × timepoints).
- **Unpaired evaluation** — every metric compares *sets* of recordings, so no one-to-one
  correspondence between real and synthetic samples is needed.
- **Per-lead breakdown** — most metrics report a score per lead in addition to the overall score.
- **Fréchet ECG Distance (FED)** — an FID-style metric on embeddings from pre-trained ECG
  foundation models (ECGFounder, HuBERT-ECG, ECG-FM).
- **Clinical feature extraction** — interval, amplitude and HRV features via NeuroKit2,
  with a SciPy/NumPy fallback.
- **Interactive reports** — ECG gallery on graph paper, per-lead bar charts, PSD overlays,
  radar chart, summary table with CSV export and 2D/3D feature plots, all in one HTML file.
- **Compare many models at once** — pass several synthetic datasets and get them side by side.

## At a glance

=== "Command line"

    ```bash
    ecgen-eval eval \
      --real real_ecgs.npy \
      --synthetic model_a.npy \
      --synthetic model_b.npy \
      -m mmd -m fd -m psd -m prd -m hrv \
      --feature-plots \
      --output report.html
    ```

=== "Python"

    ```python
    from ecgen_eval import load_ecg_npy, AVAILABLE_METRICS

    real = load_ecg_npy("real_ecgs.npy", label="PTB-XL")
    synth = load_ecg_npy("model_a.npy", label="Model A")

    result = AVAILABLE_METRICS["mmd"]().compute(
        real.data, synth.data, lead_names=real.lead_names
    )
    print(result.score, result.per_lead_scores)
    ```

## How it fits together

[![ECGEN-Eval pipeline: inputs are loaded into an ECGDataset, scored by metrics and feature extraction, and assembled into an HTML report](assets/diagrams/pipeline-light.svg#only-light){ .ecgen-diagram }](assets/diagrams/pipeline-light.svg "Open full size")
[![ECGEN-Eval pipeline: inputs are loaded into an ECGDataset, scored by metrics and feature extraction, and assembled into an HTML report](assets/diagrams/pipeline-dark.svg#only-dark){ .ecgen-diagram }](assets/diagrams/pipeline-dark.svg "Open full size")

## Citation

If you use ECGEN-Eval in your research, please cite the repository:

```bibtex
@software{thambawita_ecgen_eval,
  author = {Thambawita, Vajira},
  title  = {{ECGEN-Eval}: Evaluation metrics and interactive reports for synthetic ECG
            quality assessment},
  url    = {https://github.com/vlbthambawita/ECGEN-Eval},
}
```

ECGEN-Eval is released under the [Apache License 2.0](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/LICENSE).
