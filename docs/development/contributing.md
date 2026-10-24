# Contributing

Contributions are welcome — bug reports and feature requests go to
[GitHub Issues](https://github.com/vlbthambawita/ECGEN-Eval/issues).

## Development setup

```bash
git clone https://github.com/vlbthambawita/ECGEN-Eval.git
cd ECGEN-Eval
pip install -e ".[dev,features]"
pip install scipy wfdb
```

## Tests

```bash
pytest tests/ -v                              # all tests
pytest tests/test_metrics.py::test_mmd -v     # a single test
pytest tests/ --cov=ecgen_eval                # with coverage
```

## Code style

Line length is **100** for both tools.

```bash
black ecgen_eval/ tests/
ruff check ecgen_eval/ tests/
```

- NumPy-style docstrings (they are rendered in the [API Reference](../api/index.md)).
- Optional dependencies are imported inside functions with an `ImportError` fallback.
- Lower-is-better unless the metric sets `higher_is_better = True`.

## Documentation

The site is built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) and
[mkdocstrings](https://mkdocstrings.github.io/).

```bash
pip install -e ".[docs]"
mkdocs serve            # live preview at http://127.0.0.1:8000
mkdocs build --strict   # what CI runs
```

- Pages live in `docs/`; navigation is defined in `mkdocs.yml`.
- API pages (`docs/api/*.md`) use `::: module.path` directives and are generated from docstrings.
- Every push to `main` deploys the site to GitHub Pages via
  `.github/workflows/docs.yml`; pull requests only build it.

## Releasing

Pushing a tag `vX.Y.Z` runs the tests, builds the sdist/wheel and publishes to PyPI through
Trusted Publishing (`.github/workflows/publish.yml`). The version is derived from the tag.
