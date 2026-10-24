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

### Diagrams

Diagrams are written in [D2](https://d2lang.com) and committed as rendered SVGs, so building
the site does not require D2.

| Path | Contents |
|---|---|
| `docs/diagrams/*.d2` | Diagram sources |
| `docs/diagrams/palette-light.d2`, `palette-dark.d2` | Shared colour classes (`data`, `metric`, `feature`, `viz`, `report`, `model`, `group`, edge styles) |
| `docs/assets/diagrams/<name>-{light,dark}.svg` | Rendered output |

After editing a `.d2` file, re-render both variants:

```bash
curl -fsSL https://d2lang.com/install.sh | sh -s --   # once
bash docs/diagrams/render.sh
```

Embed a diagram so it follows the light/dark toggle:

```markdown
[![Alt text](../assets/diagrams/name-light.svg#only-light){ .ecgen-diagram }](../assets/diagrams/name-light.svg "Open full size")
[![Alt text](../assets/diagrams/name-dark.svg#only-dark){ .ecgen-diagram }](../assets/diagrams/name-dark.svg "Open full size")
```

### Version and changelog

The version badge in the header and footer comes from the latest git tag
(`hooks/docs_version.py`); write `\{{ ecgen_version }}` in a page to insert it. Record
user-facing changes under **Unreleased** in `docs/changelog.md`, and move them into a new
version section when tagging a release.

## Releasing

Pushing a tag `vX.Y.Z` runs the tests, builds the sdist/wheel and publishes to PyPI through
Trusted Publishing (`.github/workflows/publish.yml`). The version is derived from the tag.
