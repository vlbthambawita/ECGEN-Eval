# Installation

ECGEN-Eval is tested on **Python 3.9 and 3.11**; Python 3.9 or newer is recommended.

## From source

```bash
git clone https://github.com/vlbthambawita/ECGEN-Eval.git
cd ECGEN-Eval
pip install -e .
```

This installs the core package and the `ecgen-eval` command. Core dependencies are
`numpy`, `pandas`, `plotly`, `click`, `jinja2`, `tqdm`, `scikit-learn` and `dtaidistance`.

## From PyPI

Tagged releases (`v*`) are published to PyPI automatically:

```bash
pip install ecgen-eval                       # latest release (currently {{ ecgen_version }})
pip install "ecgen-eval=={{ ecgen_version }}"   # pin this exact version
```

## Optional extras

Some functionality depends on heavier packages that are not installed by default.

| Extra | Command | Adds | Needed for |
|---|---|---|---|
| `features` | `pip install -e ".[features]"` | `neurokit2`, `scipy` | Clinical feature extraction, `--feature-plots`, the `features` CLI command |
| `fed` | `pip install -e ".[fed]"` | `torch`, `transformers`, `huggingface_hub` | The `fed` metric (Fréchet ECG Distance) |
| `dev` | `pip install -e ".[dev]"` | `pytest`, `pytest-cov`, `black`, `ruff` | Running tests and linting |
| `docs` | `pip install -e ".[docs]"` | `mkdocs-material`, `mkdocstrings[python]` | Building this documentation |

Extras can be combined:

```bash
pip install -e ".[features,fed,dev]"
```

### Other optional packages

| Package | Install | Effect |
|---|---|---|
| `scipy` | `pip install scipy` | Welch PSD (`psd`, `spectral_entropy`), `find_peaks` R-peak detection (`hrv`, `heart_rate`), and resampling in `load_ecg_wfdb(resample_to=...)`. Without it, plain FFT and NumPy fallbacks are used. |
| `wfdb` | `pip install wfdb` | Loading WFDB records such as PTB-XL. |

!!! tip "Fallbacks"
    Optional dependencies are imported inside the functions that need them. If one is
    missing, ECGEN-Eval falls back to a simpler implementation where one exists (FFT instead
    of Welch, a NumPy peak detector instead of SciPy) and raises an `ImportError` with an
    install hint where none exists (WFDB loading, FED).

## Foundation-model weights

The `fed` metric downloads model weights from the Hugging Face Hub **the first time it is
computed** and caches them locally. Nothing is downloaded at import time.

```bash
export HF_HOME=/path/to/large/disk/hf-cache   # optional: change cache location
```

See [Fréchet ECG Distance](../user-guide/fed.md) for details on each backbone.

## Verify the installation

```bash
ecgen-eval --version
ecgen-eval list-metrics
```

and, from a source checkout:

```bash
pytest tests/ -v
```
