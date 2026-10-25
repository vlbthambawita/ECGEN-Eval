# Installation

ECGEN-Eval is tested on **Python 3.9 and 3.11**; Python 3.9 or newer is recommended.

## Install from PyPI

ECGEN-Eval is published on [PyPI](https://pypi.org/project/ecgen-eval/):

```bash
pip install ecgen-eval                       # latest release (currently {{ ecgen_version }})
pip install "ecgen-eval=={{ ecgen_version }}"   # pin this exact version
pip install --upgrade ecgen-eval             # upgrade an existing install
```

This installs the core package and the `ecgen-eval` command. Core dependencies are
`numpy`, `pandas`, `plotly`, `click`, `jinja2`, `tqdm`, `scikit-learn` and `dtaidistance`.
Check the installed version with `pip show ecgen-eval`.

## Optional extras

Some functionality depends on heavier packages that are not installed by default.

| Extra | Command | Adds | Needed for |
|---|---|---|---|
| `features` | `pip install "ecgen-eval[features]"` | `neurokit2`, `scipy` | Clinical feature extraction, `--feature-plots`, the `features` CLI command |
| `fed` | `pip install "ecgen-eval[fed]"` | `torch`, `transformers`, `huggingface_hub` | The `fed` metric (Fréchet ECG Distance) |

Extras can be combined:

```bash
pip install "ecgen-eval[features,fed]"
```

The quotes stop shells such as zsh from treating the square brackets as a glob pattern.

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
pip show ecgen-eval      # installed version
ecgen-eval list-metrics
```

!!! note
    `ecgen-eval --version` reports `0.1.0` in releases up to 0.5.0 because of a bug that is
    fixed for the next release. Use `pip show ecgen-eval` to see the real version.

and, from a source checkout:

```bash
pytest tests/ -v
```

## Development install

To change ECGEN-Eval itself, run the tests or build this documentation, install from a
clone instead. The `dev` and `docs` extras are meant for this:

```bash
git clone https://github.com/vlbthambawita/ECGEN-Eval.git
cd ECGEN-Eval
pip install -e ".[dev,features]"   # add docs to build the documentation
```

See [Contributing](../development/contributing.md) for the full workflow.
