# Loading Data

All of ECGEN-Eval operates on an [`ECGDataset`](../api/data.md#ecgen_eval.data.dataset.ECGDataset):
a NumPy array of shape **`(N, L, T)`** plus metadata. Loaders read files from disk and
normalise them into this container.

## The `ECGDataset` container

| Attribute | Type | Meaning |
|---|---|---|
| `data` | `np.ndarray` `(N, L, T)` | Signals (cast to `float32` by the loaders) |
| `lead_names` | `list[str]` | Ordered lead names, length `L` |
| `fs` | `float` | Sampling frequency in Hz |
| `source_path` | `Path` | Where the data came from |
| `label` | `str` | Name used in plots and reports |
| `file_names` | `list[str]` | Original file name per recording |

Convenience properties: `n_samples`, `n_leads`, `n_timepoints`, `duration_sec`, `time_axis`.

```python
ds = load_ecg_npy("real.npy")
ds.n_samples, ds.n_leads, ds.duration_sec      # (100, 12, 10.0)

limb = ds.select_leads(["I", "II", "III"])     # new dataset with 3 leads
small = ds.sample(20, seed=0)                  # 20 random recordings
```

You can also construct one directly from an array you already have in memory:

```python
from pathlib import Path
from ecgen_eval.data.dataset import ECGDataset, LEADS_12

ds = ECGDataset(data=arr, lead_names=LEADS_12, fs=500.0,
                source_path=Path("."), label="My model")
```

## Loaders at a glance

| Function | Input | Typical use |
|---|---|---|
| [`load_ecg_npy`](../api/data.md#ecgen_eval.data.loader.load_ecg_npy) | one `.npy` / `.npz` file | Output of ECGEN-FM, ECGEN-VAE, Pulse2Pulse |
| [`load_ecg_wfdb`](../api/data.md#ecgen_eval.data.loader.load_ecg_wfdb) | directory of `.hea`/`.dat` records | PTB-XL and other PhysioNet datasets |
| [`load_ecg_folder`](../api/data.md#ecgen_eval.data.loader.load_ecg_folder) | file or directory, auto-detected | Anything — this is what the CLI uses |

All loaders accept `fs`, `label`, `lead_names` and `max_samples` (cap on recordings loaded).

## NumPy

```python
from ecgen_eval import load_ecg_npy

ds = load_ecg_npy("synth.npy", fs=500, label="ECGEN-FM", max_samples=1000)
```

- A 3-D array `(N, L, T)` is used as is; a 2-D array `(L, T)` is treated as one recording.
- For `.npz` archives, the array whose key equals `label` is used if present, otherwise the first array.
- `label` defaults to the file stem.

## WFDB (PTB-XL, PhysioNet)

Requires `pip install wfdb`.

```python
from ecgen_eval import load_ecg_wfdb

ptbxl = load_ecg_wfdb("ptb-xl/records500/00000", label="PTB-XL", max_samples=500)

# Resample on load (requires scipy)
ptbxl_250 = load_ecg_wfdb("ptb-xl/records500/00000", resample_to=250)
```

- Lead names are read from the record header (`sig_name`) unless you pass `lead_names`.
- The sampling rate is taken from the header; `fs` is only a fallback.
- `record_dir` may also be a single record path without extension.
- Unreadable records are skipped silently.

## Auto-detection with `load_ecg_folder`

`load_ecg_folder` inspects the path and dispatches in this order:

1. A single `.npy` / `.npz` file → `load_ecg_npy`.
2. A directory with `*.npy` files (or else `*.npz`) → every file is loaded and stacked.
   Each file may hold one `(L, T)` recording or a batch `(N, L, T)`.
3. A directory with `*.hea` files → `load_ecg_wfdb`.
4. Otherwise → CSV loading (single `.csv` file or a directory of them).

```python
from ecgen_eval import load_ecg_folder

ds = load_ecg_folder("outputs/model_a/", fs=500, label="Model A")
```

## CSV layouts

The CSV loader detects one of three layouts from the first file:

=== "A) Wide — one file per recording"

    Rows are leads, columns are timepoints (shape on disk `L × T`). An optional
    index column is dropped.

    ```text
    0.01,0.02,0.05,...     ← lead I
    0.00,0.03,0.07,...     ← lead II
    ...
    ```

=== "B) Flat — one file per recording"

    A single row of `L × T` values. Columns may be named `<lead>_<index>`, e.g.
    `I_0, I_1, …, V6_4999`; lead names are then parsed from the header.

    ```text
    I_0,I_1,...,I_4999,II_0,...,V6_4999
    0.01,0.02,...
    ```

=== "C) Multi-recording flat — one file per dataset"

    Like (B), but each row is a whole recording.

    ```text
    I_0,I_1,...,V6_4999
    0.01,0.02,...          ← recording 0
    0.03,0.01,...          ← recording 1
    ```

If detection fails, pass `n_leads` and `n_timepoints` explicitly:

```python
ds = load_ecg_folder("csv_dir/", n_leads=12, n_timepoints=5000)
```

## Default lead names

When no lead names are supplied or found:

| Leads | Names |
|---|---|
| 12 | `I, II, III, aVR, aVL, aVF, V1, V2, V3, V4, V5, V6` (`LEADS_12`) |
| 8 | `I, II, V1, V2, V3, V4, V5, V6` (`LEADS_8`) |
| other | generic names |

!!! tip "Matching real and synthetic data"
    Metrics require the **same number of leads** in real and synthetic data and raise a
    `ValueError` otherwise. They do not require the same number of recordings. Most metrics
    also compare signals sample by sample or use the same feature extractor on both sets, so
    real and synthetic recordings should share sampling rate, length, units and lead order.
    Use `select_leads` and `load_ecg_wfdb(resample_to=...)` to align them.
