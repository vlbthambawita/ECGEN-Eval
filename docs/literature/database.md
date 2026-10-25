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

<div id="litdb" data-src="../papers.json"></div>

## Data files

The database is generated from the review's `papers_index.csv` by
`literature_review_claude/build_db.py` and committed with the documentation:

- [`papers.json`](papers.json): the full database used by this page
- [`papers.csv`](papers.csv): the same data as a spreadsheet

To rebuild it after adding papers:

```bash
python literature_review_claude/build_db.py         # papers with full text
python literature_review_claude/build_db.py --all   # also include abstract-only entries
```
