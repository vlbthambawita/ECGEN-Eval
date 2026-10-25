---
hide:
  - navigation
  - toc
---

# Paper Database

Interactive database of the papers in the [literature review](index.md). Use the search box
and the filters to narrow the list, then click a paper to see its model, loss functions,
evaluation metrics, datasets and notes.

- Filters within a group match **any** selected value by default; click *match ANY* to switch a
  group to *match ALL* (e.g. papers that use both FID **and** a Turing test).
- The number next to each value shows how many papers would match if you selected it.
- The bars summarise metrics and losses in the currently filtered papers.
- Metric and loss families are assigned automatically from the extracted text. Check the
  original paper before citing a detail.

<div id="litdb" data-src="../ecgen_literature.sqlite"
     data-sqljs="https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.10.3/sql-wasm.js"></div>

## The SQLite database

The page opens the database directly in your browser with
[sql.js](https://sql.js.org) (SQLite compiled to WebAssembly). Nothing is sent to a server.
Use the **SQL console** above for queries the filters can't express.

- [`ecgen_literature.sqlite`](ecgen_literature.sqlite): the database (open it with `sqlite3`,
  DB Browser for SQLite, pandas, …)
- [`papers.csv`](papers.csv): one flat row per paper, for spreadsheets

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
| `papers` | One row per paper: bibliographic data, model family, task, datasets, signal shape, verbatim extracted `loss_functions` and `eval_metrics`, notes and takeaway for ECGEN-Eval |
| `authors`, `paper_authors` | Authors and their order on each paper |
| `facets` | Filter dimensions: `category`, `year`, `metric_type`, `metric`, `loss`, `task`, `dataset`, `extraction_source` |
| `terms` | Values of each facet. `parent_id` links a metric to its metric type, and `ecgen_eval` names the matching ECGEN-Eval metric key |
| `paper_terms` | Which terms apply to which paper |
| `paper_facets` (view) | One row per (paper, facet, term), the easiest table to query |
| `metric_usage` (view) | Each metric family with its type, ECGEN-Eval coverage and number of papers |
| `meta` | Build date, scope and source |

Example: papers that use both an embedding FID and a Turing test.

```sql
SELECT p.id, p.year, p.title
FROM papers p
WHERE p.id IN (SELECT paper_id FROM paper_facets WHERE facet = 'metric' AND term = 'FID / embedding Fréchet')
  AND p.id IN (SELECT paper_id FROM paper_facets WHERE facet = 'metric' AND term = 'Expert / Turing test');
```

### Rebuilding

The database is generated from the review's `papers_index.csv` by
`literature_review_claude/build_db.py`:

```bash
python literature_review_claude/build_db.py         # papers with full text
python literature_review_claude/build_db.py --all   # also include abstract-only entries
```
