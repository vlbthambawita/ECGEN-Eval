# ECG feature-extractor catalogue (source data)

Curated data behind the `extractor*` tables of `docs/literature/ecgen_literature.sqlite`.
The narrative review is `../04_ecg_feature_extractors.md`; `../build_db.py` loads these files.

| File | Contents |
|---|---|
| `feature_vocab.csv` | Canonical feature vocabulary (`id`, `group`, `name`, `unit`, `ecgen_eval_column`, `description`). Every tool feature maps to one of these ids, so tools can be compared feature by feature and matched to ECGEN-Eval's `summary_df` columns. |
| `tools.jsonl` | One JSON object per tool (schema below). |

## `tools.jsonl` schema

```jsonc
{
  "id": "X001",                       // stable id
  "name": "NeuroKit2",
  "category": "delineation",          // delineation | dl_delineation | rpeak | hrv | sqi |
                                      // ml_table | generic_ts | non_python | reference_measurements
  "url": "https://github.com/...",
  "pypi": "neurokit2",                // "" if not on PyPI
  "install": "pip install neurokit2",
  "license": "MIT",
  "license_class": "permissive",      // permissive | copyleft | none | noncommercial | proprietary
  "version": "0.2.13", "release_date": "2026-03-02",
  "maintained": "yes",                // yes | stale | unknown
  "language": "Python",               // implementation language(s)
  "python_requires": ">=3.8",
  "runtime_deps": "numpy, scipy, pandas",   // notable heavy / non-Python dependencies
  "paper_citation": "Makowski et al., Behav Res Methods 2021", "paper_doi": "10.3758/...",
  "method": "short description of the algorithm(s)",
  "input": {
    "signal_types": ["ECG", "PPG"],
    "input_kinds": ["raw_1d"],        // raw_1d | raw_multilead | wfdb_record | csv | edf | mat |
                                      // rpeaks | rr_intervals | image
    "shape": "1-D array (n_samples,)",
    "multilead": "per-lead",          // native | per-lead | single-lead
    "fs_param": "sampling_rate",      // argument name, "" if fixed
    "fs_default": 1000,               // null if required / none
    "fs_supported": "any (user supplied)",
    "fs_min_recommended": 250,        // null if not stated
    "fs_notes": "...",
    "min_duration_s": 10, "duration_notes": "...",
    "amplitude_units": "mV (unit-agnostic except thresholds)",
    "preprocessing": "built-in cleaning ...",
    "batch": "one record per call"
  },
  "output": {"format": "pandas DataFrame + dict", "levels": ["beat", "record"]},
  "features": [
    {"feature": "p_onset", "native": "ECG_P_Onsets", "api": "nk.ecg_delineate(method='dwt')",
     "level": "beat", "notes": ""}
  ],
  "other_outputs": "native outputs that have no vocabulary id",
  "n_features_reported": 22,          // as the tool / paper states it, null if not stated
  "evidence": ["URLs or source files read"],
  "verified": "source",               // source | docs | paper | readme
  "notes": "caveats relevant to using it inside ECGEN-Eval"
}
```
