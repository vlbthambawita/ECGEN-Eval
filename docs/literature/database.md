---
hide:
  - navigation
  - toc
---

# Paper Database

Interactive database of the papers in the [literature review](index.md), plus a catalogue of
open-source ECG feature extractors. It has four views:

- **Papers**: filter by model category, year, evaluation category, evaluation metric, loss
  function, task, conditioning, data type, data format, number of leads, sampling rate,
  segment length, dataset, data access, code availability and publication type. Click a paper
  to see each metric it uses, how it was used, and any fairness, robustness or privacy
  analysis.
- **Metrics by evaluation category**: pick *Fidelity*, *Diversity*, *Utility*, *Privacy*,
  *Fairness*, *Robustness*, *Clinical validity*, *Human / expert*, *Conditional consistency* or
  *Efficiency* to list the metric families in that category, the number of papers using
  each, and whether ECGEN-Eval implements it. Click a metric to list the papers and how
  each one used it. The filters on the Papers tab also apply here.
- **Feature extractors**: open-source ECG feature tools usable from Python (and the published
  reference measurements in PTB-XL+). Filter by category, licence, input type, lead support
  and by the features you need; click a tool for its accepted inputs, sampling-rate handling,
  minimum duration, native output names and the API that produces each feature.
- **SQL console**: run read-only SQL against the database.

Quick links: [Fidelity](#metrics/Fidelity) · [Diversity](#metrics/Diversity) ·
[Utility](#metrics/Utility) · [Privacy](#metrics/Privacy) · [Fairness](#metrics/Fairness) ·
[Robustness](#metrics/Robustness) · [Clinical validity](#metrics/Clinical%20validity) ·
[Feature extractors](#extractors)

!!! note "How the data was produced"
    Every paper was read in full text. Each metric was recorded as the paper names it, then
    mapped to a canonical metric family and one or two evaluation categories. Some fields were
    judgement calls, so check the original paper before citing a detail. Filters within a group
    match **any** selected value by default; click *match ANY* to switch the group to
    *match ALL*.

<div id="litdb" data-src="../ecgen_literature.sqlite"
     data-sqljs="https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.10.3/sql-wasm.js"></div>

## The SQLite database

The page opens the database directly in your browser with
[sql.js](https://sql.js.org) (SQLite compiled to WebAssembly). Nothing is sent to a server.
Use the **SQL console** above for queries the filters can't express.

- [`ecgen_literature.sqlite`](ecgen_literature.sqlite): the database (open it with `sqlite3`,
  DB Browser for SQLite, pandas, …)
- [`papers.csv`](papers.csv): one flat row per paper, for spreadsheets
- [`feature_extractors.csv`](feature_extractors.csv): one row per feature extractor with its
  input specification
- [`feature_support_matrix.csv`](feature_support_matrix.csv): canonical feature × extractor
  matrix (`x` = the tool returns that feature)

```python
import sqlite3
con = sqlite3.connect("ecgen_literature.sqlite")
con.execute("SELECT * FROM metric_usage").fetchall()
```

### Schema

The schema stores filter dimensions as data, so new categories, metric families or whole new
facets are added as rows rather than new tables:

| Table / view | Contents |
|---|---|
| `papers` | One row per paper: bibliographic data, model family, task, datasets, leads, sampling rate and segment length, verbatim `loss_functions` and `eval_metrics`, descriptions of any `fairness` / `robustness` / `privacy` analysis, notes and takeaway for ECGEN-Eval |
| `evaluations` | One row per metric or protocol a paper uses: name as in the paper, canonical metric family, and how it was used |
| `evaluation_categories` | Evaluation categories of each evaluation (Fidelity, Diversity, Utility, Privacy, Fairness, Robustness, Clinical validity, Human / expert, Conditional consistency, Efficiency) |
| `authors`, `paper_authors` | Authors and their order on each paper |
| `facets` | Filter dimensions, e.g. `category`, `year`, `eval_category`, `metric`, `loss`, `task`, `conditioning`, `data_type`, `data_format`, `leads`, `sampling_rate`, `segment_length`, `dataset`, `data_access`, `code`, `venue_type` |
| `terms` | Values of each facet. For metrics, `parent_id` is the default evaluation category and `ecgen_eval` names the matching ECGEN-Eval metric key; categories have a `description` |
| `paper_terms` | Which terms apply to which paper |
| `paper_facets` (view) | One row per (paper, facet, term), the easiest table to filter on |
| `evaluation_details` (view) | One row per (evaluation, category) with paper, metric name, family, ECGEN-Eval key and how it was used |
| `metric_usage` (view) | Papers per (evaluation category, metric family), with ECGEN-Eval coverage |
| `meta` | Build date, scope and source |

Feature-extractor catalogue (independent of the paper tables):

| Table / view | Contents |
|---|---|
| `extractors` | One row per tool: category, links, install command, licence and licence class (`permissive`, `copyleft`, `none`, `noncommercial`, `proprietary`), version, language and runtime, paper, method, notes |
| `extractor_inputs` | What the tool accepts: signal types, input kinds, array shape, multi-lead support, sampling-rate argument / default / supported range / recommended minimum, minimum duration, amplitude units, built-in preprocessing, output format and level |
| `extractor_input_kinds`, `extractor_signal_types` | One row per input kind (`raw_1d`, `raw_multilead`, `wfdb_record`, `csv`, `rpeaks`, `rr_intervals`, …) or signal type, for filtering |
| `feature_vocab` | Canonical feature vocabulary (fiducial points, intervals, amplitudes, axes, HRV, signal quality, …). `ecgen_eval_column` links a feature to ECGEN-Eval's `summary_df` column |
| `extractor_features` | One row per (tool, canonical feature, API): the tool's native output name(s), the function that produces them and the level (beat, lead, record, window) |
| `extractor_evidence` | Source files, docs and papers read to verify each entry |
| `extractor_feature_details` (view) | Tool + feature + native name + API in one row |
| `feature_coverage` (view) | For each canonical feature, how many tools provide it and which |
| `ecgen_feature_support` (view) | For each ECGEN-Eval feature column, every tool that can provide it, with its input requirements |

Example: privacy metrics and the papers that use them.

```sql
SELECT family, metric_name, paper_id, year, how
FROM evaluation_details
WHERE category = 'Privacy'
ORDER BY family, year DESC;
```

Example: papers that use both an embedding FID and a Turing test.

```sql
SELECT p.id, p.year, p.title
FROM papers p
WHERE p.id IN (SELECT paper_id FROM paper_facets WHERE facet = 'metric' AND term = 'FID / embedding Fréchet')
  AND p.id IN (SELECT paper_id FROM paper_facets WHERE facet = 'metric' AND term = 'Expert / Turing test');
```

Example: permissively licensed tools that return both QRS onset and T offset (needed for QT)
and how they take the sampling rate.

```sql
SELECT x.name, x.license, i.input_kinds, i.multilead, i.fs_param, i.fs_supported
FROM extractors x JOIN extractor_inputs i ON i.extractor_id = x.id
WHERE x.license_class = 'permissive'
  AND x.id IN (SELECT extractor_id FROM extractor_features WHERE feature_id = 'qrs_onset')
  AND x.id IN (SELECT extractor_id FROM extractor_features WHERE feature_id = 't_offset');
```

### Rebuilding

The database is generated by `literature_review_claude/build_db.py` from the review's
`papers_index.csv` and the per-metric records in `structured_extraction.jsonl`. The extractor
catalogue comes from `literature_review_claude/feature_extractors/` (`feature_vocab.csv` and
`tools.jsonl`; see its README for the record schema):

```bash
python literature_review_claude/build_db.py         # papers with full text
python literature_review_claude/build_db.py --all   # also include abstract-only entries
```
