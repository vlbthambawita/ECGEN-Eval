# Command-Line Interface

Installing the package provides the `ecgen-eval` command, with five sub-commands:

| Command | Purpose |
|---|---|
| [`eval`](#eval) | Compute metrics and write an interactive HTML report |
| [`features`](#features) | Extract clinical features and write a CSV |
| [`visualize`](#visualize) | ECG waveform comparison only, no metrics |
| [`list-metrics`](#list-metrics) | Print the available metrics |
| [`list-features`](#list-features) | Print the clinical feature groups and extraction backends |

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
| `-m, --metrics KEY` | curated set of 12 | Metric to compute. Repeatable. `all` runs every metric except `fed`. See `list-metrics` |
| `-o, --output PATH` | `ecgen_eval_report.html` | Report path |
| `--fs FLOAT` | `500.0` | Sampling frequency (Hz) of the data; also passed to `psd`, `spectral_entropy`, `hrv`, `heart_rate`, `pearson`, `curve_frechet` |
| `--pairing` | `nn` | How `mse`, `rmse`, `euclidean`, `pearson`, `cosine` and `curve_frechet` match signals: `nn` (nearest neighbour), `paired` (recording *i* with recording *i*; needs equal counts) or `mean` (mean waveforms). See [Matching protocol](metric-reference.md#matching-protocol) |
| `--n-samples INT` | `3` | Recordings shown in the ECG gallery |
| `--leads TEXT` | all | Comma-separated leads for the gallery, e.g. `I,II,V1` |
| `--compare-mode` | `overlay` | `overlay`, `sidebyside` or `grid` |
| `--max-samples INT` | — | Cap on recordings loaded per dataset (quick tests) |
| `--offline` | off | Embed Plotly.js so the report works without internet |
| `--real-label TEXT` | file/folder name | Display label for the real set |
| `--synth-labels TEXT` | file/folder names | Comma-separated labels, in `--synthetic` order |
| `--gallery-selection` | `first` | Recordings shown in the gallery: `first` or `random` (fixed seed; the indices are printed in the report) |
| `--beat-bands / --no-beat-bands` | on | Beat morphology section: median and 5–95 % band of all detected beats |
| `--embedding-plots` | off | Add 2-D [embedding projections](visualization.md#embedding-projections) of real vs synthetic recordings |
| `--embedding-method` | `pca` | `pca`, `tsne` or `umap` (needs `[umap]`). Repeatable |
| `--embedding-features` | `handcrafted` | `handcrafted` (11 signal features per lead), `signal` (waveform) or `clinical` (runs feature extraction) |
| `--feature-plots` | off | Extract clinical features and add summary table (with KS statistics) + 2D/3D plots (needs `[features]`) |
| `-F, --feature`, `--feature-backend`, `--rpeak-method`, `--delineation-method` | all / `hybrid` | Which features and which library, with `--feature-plots`; see [Feature options](#feature-options) |
| `--backbone` | `ecgfounder` | FED backbone: `ecgfounder`, `hubert_ecg`, `ecgfm` |
| `--fed-device TEXT` | `cpu` | PyTorch device for FED, e.g. `cuda` |
| `--fed-batch-size INT` | `32` | FED batch size |

!!! note "Default metric set"
    Without `-m`, a curated set of 12 metrics runs: one or two per evaluation question, with
    no near-duplicates.

    | Question | Metrics |
    |---|---|
    | Does the population match? | `fd`, `mmd` |
    | Realism and coverage? | `pr_dist` |
    | Can a classifier tell them apart? | `c2st` |
    | Do waveforms match? | `rmse`, `pearson`, `dtw` |
    | Are amplitudes right? | `js_div` |
    | Is the frequency content right? | `psd` |
    | Is the rhythm physiological? | `heart_rate`, `hrv` |
    | Is the model copying? | `nn_dist` |

    `-m all` runs every registered metric except `fed` (24 metrics). `fed` requires the
    `[fed]` extra and downloads model weights, so it always has to be named: `-m fed`, or
    `-m all -m fed` for everything. The metrics left out of the default either repeat one
    that is in it (`mse`, `euclidean`, `mae`, `prd`, `psnr` against `rmse`; `swd`, `ks_test`
    against `mmd`; `spectral_entropy` against `psd`; `sqi`, `ssim` against `pearson`) or
    separate generators poorly (`cosine`, `curve_frechet`). Request them with `-m` when you
    need to reproduce a number from a paper.

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

# Paired data (e.g. reconstructed leads): compare recording i with recording i
ecgen-eval eval -r real.npy -s reconstructed.npy --pairing paired \
  -m rmse -m pearson -m curve_frechet -o paired.html

# Paper-style fidelity set plus PCA and t-SNE projections
ecgen-eval eval -r real.npy -s synth.npy -m rmse -m pearson -m js_div -m ks_test -m c2st \
  --embedding-plots --embedding-method pca --embedding-method tsne -o fidelity.html

# Every metric, including FED
ecgen-eval eval -r real.npy -s synth.npy -m all -m fed -o everything.html

# Include clinical feature distributions
ecgen-eval eval -r real.npy -s synth.npy -m mmd -m hrv --feature-plots -o features.html

# Feature plots of intervals and heart rate only, delineated with plain NeuroKit2 DWT
ecgen-eval eval -r real.npy -s synth.npy -m mmd --feature-plots \
  -F intervals -F hr_bpm --feature-backend neurokit2 --delineation-method dwt
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
| `--stats-output PATH` | — | Also write a CSV of two-sample tests (KS, Mann–Whitney U, Cohen's d) between the real and each synthetic feature distribution; see [Statistical comparison](features.md#statistical-comparison) |
| `-F, --feature`, `--feature-backend`, `--rpeak-method`, `--delineation-method` | all / `hybrid` | See [Feature options](#feature-options) |

```bash
ecgen-eval features -r real.npy -s synth.npy --lead II -o features.csv

# Only HRV and QTc, SciPy-only R peaks (no NeuroKit2 needed)
ecgen-eval features -r real.npy -s synth.npy -F hrv -F qtc_bazett_ms --feature-backend scipy
```

### Feature options

Shared by `features` and `eval --feature-plots`:

| Option | Default | Description |
|---|---|---|
| `-F, --feature TEXT` | all groups | Feature group (`rhythm`, `intervals`, `hrv`, `amplitude`) or single column (e.g. `qtc_bazett_ms`). Repeatable |
| `--feature-backend` | `hybrid` | Library that finds beats and P/QRS/T boundaries: `hybrid`, `neurokit2` or `scipy` |
| `--rpeak-method TEXT` | backend default | `nk.ecg_peaks` method (`neurokit`, `pantompkins1985`, `hamilton2002`, `elgendi2010`, …) or `scipy` |
| `--delineation-method` | backend default | `nk.ecg_delineate` method: `prominence`, `dwt`, `cwt`, `peak` |

See [Clinical Features → Choosing features and libraries](features.md#choosing-features-and-libraries).

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
| `--compare-mode` | `overlay` | `overlay`, `sidebyside`, `grid` (individual recordings), `beats` (median and 5–95 % band of all R-peak-aligned beats) or `beat-density` (their density maps) |
| `--show-r-peaks` | off | Mark detected R peaks on every trace |
| `--embedding` | — | Add a 2-D projection of 11 signal features per lead: `pca`, `tsne` or `umap`. Repeatable |
| `--max-samples INT` | — | Cap on recordings loaded |
| `--offline` | off | Embed Plotly.js |

```bash
ecgen-eval visualize -r real.npy -s synth.npy --compare-mode grid --n-samples 5

# All beats instead of a few recordings, plus a PCA projection
ecgen-eval visualize -r real.npy -s synth.npy --compare-mode beats --embedding pca
```

## `list-metrics`

```bash
ecgen-eval list-metrics
```

Prints every metric key with its description and reference.

## `list-features`

```bash
ecgen-eval list-features
```

Prints every feature group with its columns, and every extraction backend with the
libraries it needs.
