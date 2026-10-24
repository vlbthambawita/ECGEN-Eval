# Command-Line Interface

Installing the package provides the `ecgen-eval` command, with four sub-commands:

| Command | Purpose |
|---|---|
| [`eval`](#eval) | Compute metrics and write an interactive HTML report |
| [`features`](#features) | Extract clinical features and write a CSV |
| [`visualize`](#visualize) | ECG waveform comparison only, no metrics |
| [`list-metrics`](#list-metrics) | Print the available metrics |

```bash
ecgen-eval --help
ecgen-eval --version
ecgen-eval eval --help
```

Every `--real` / `--synthetic` path is loaded with
[`load_ecg_folder`](data-loading.md#auto-detection-with-load_ecg_folder), so it can be a
`.npy`/`.npz` file, a folder of NumPy files, a WFDB folder or CSV data.

!!! warning "Repeatable options"
    `--synthetic` and `--metrics` are **repeatable**: give the flag once per value.

    ```bash
    -s a.npy -s b.npy -m mmd -m fd      # correct
    -s a.npy b.npy --metrics mmd fd     # error: unexpected extra argument
    ```

## `eval`

Run metrics and generate a report.

```bash
ecgen-eval eval --real REAL --synthetic SYNTH [--synthetic SYNTH2 ...] [OPTIONS]
```

| Option | Default | Description |
|---|---|---|
| `-r, --real PATH` | *required* | Real ECG data |
| `-s, --synthetic PATH` | *required* | Synthetic ECG data. Repeatable |
| `-m, --metrics KEY` | all except `fed` | Metric to compute. Repeatable. See `list-metrics` |
| `-o, --output PATH` | `ecgen_eval_report.html` | Report path |
| `--fs FLOAT` | `500.0` | Sampling frequency (Hz) of the data; also passed to `psd`, `spectral_entropy`, `hrv`, `heart_rate` |
| `--n-samples INT` | `3` | Recordings shown in the ECG gallery |
| `--leads TEXT` | all | Comma-separated leads for the gallery, e.g. `I,II,V1` |
| `--compare-mode` | `overlay` | `overlay`, `sidebyside` or `grid` |
| `--max-samples INT` | — | Cap on recordings loaded per dataset (quick tests) |
| `--offline` | off | Embed Plotly.js so the report works without internet |
| `--real-label TEXT` | file/folder name | Display label for the real set |
| `--synth-labels TEXT` | file/folder names | Comma-separated labels, in `--synthetic` order |
| `--feature-plots` | off | Extract clinical features and add summary table + 2D/3D plots (needs `[features]`) |
| `--backbone` | `ecgfounder` | FED backbone: `ecgfounder`, `hubert_ecg`, `ecgfm` |
| `--fed-device TEXT` | `cpu` | PyTorch device for FED, e.g. `cuda` |
| `--fed-batch-size INT` | `32` | FED batch size |

!!! note "Default metric set"
    Without `-m`, every registered metric runs **except `fed`**, which requires the `[fed]`
    extra and downloads model weights. Add `-m fed` (or list it with others) to include it.

!!! note "Sampling rate"
    Metrics that take a sampling rate (`psd`, `spectral_entropy`, `hrv`, `heart_rate`) and the
    report's PSD axes use the real dataset's rate: the `--fs` value for NumPy/CSV data, or the
    rate in the headers for WFDB data. A warning is printed if a synthetic dataset's rate
    differs from the real one.

If feature extraction fails with `--feature-plots` (e.g. NeuroKit2 is missing) a warning is
printed and the report is generated without the feature sections.

### Examples

```bash
# Quick sanity check on 200 recordings
ecgen-eval eval -r real.npy -s synth.npy -m mmd -m fd -m psd --max-samples 200 -o quick.html

# Two models, custom labels, side-by-side gallery for four leads
ecgen-eval eval -r ptbxl/ -s fm.npy -s vae.npy \
  --real-label PTB-XL --synth-labels "ECGEN-FM,ECGEN-VAE" \
  --leads I,II,V1,V5 --compare-mode sidebyside --n-samples 5 \
  -m fd -m mmd -m pr_dist -m hrv -m nn_dist -o models.html

# FED on GPU with HuBERT-ECG, offline-capable report
ecgen-eval eval -r real.npy -s synth.npy -m fed -m fd \
  --backbone hubert_ecg --fed-device cuda --fed-batch-size 64 --offline -o fed.html

# Include clinical feature distributions
ecgen-eval eval -r real.npy -s synth.npy -m mmd -m hrv --feature-plots -o features.html
```

## `features`

Extract clinical features and save one CSV for all datasets, with a `dataset` column.

```bash
ecgen-eval features --real REAL [--synthetic SYNTH ...] [OPTIONS]
```

| Option | Default | Description |
|---|---|---|
| `-r, --real PATH` | *required* | Real ECG data |
| `-s, --synthetic PATH` | — | Synthetic ECG data. Repeatable, optional |
| `-o, --output PATH` | `ecg_features.csv` | Output CSV |
| `--fs FLOAT` | `500.0` | Sampling frequency (Hz) |
| `--max-samples INT` | — | Cap on recordings per dataset |
| `--lead TEXT` | `II` | Lead used for R-peak detection and interval timing |

```bash
ecgen-eval features -r real.npy -s synth.npy --lead II -o features.csv
```

## `visualize`

Waveform comparison plots only — fast, no metrics.

```bash
ecgen-eval visualize --real REAL --synthetic SYNTH [OPTIONS]
```

| Option | Default | Description |
|---|---|---|
| `-r, --real PATH` | *required* | Real ECG data |
| `-s, --synthetic PATH` | *required* | Synthetic ECG data. Repeatable |
| `-o, --output PATH` | `ecg_comparison.html` | Output HTML |
| `--fs FLOAT` | `500.0` | Sampling frequency (Hz) |
| `--n-samples INT` | `3` | Recordings to plot |
| `--leads TEXT` | all | Comma-separated leads |
| `--compare-mode` | `overlay` | `overlay`, `sidebyside` or `grid` |
| `--max-samples INT` | — | Cap on recordings loaded |
| `--offline` | off | Embed Plotly.js |

```bash
ecgen-eval visualize -r real.npy -s synth.npy --compare-mode grid --n-samples 5
```

## `list-metrics`

```bash
ecgen-eval list-metrics
```

Prints every metric key with its description and reference.
