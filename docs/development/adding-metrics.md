# Adding a Metric

New metrics plug into the CLI, the report and the radar chart automatically once they are
registered.

## 1. Implement `BaseMetric`

Create `ecgen_eval/metrics/my_metric.py`:

```python
"""
My Metric for ECG evaluation.

Reference
---------
Author, A. (2025). Title. *Venue*. https://doi.org/...
"""

from __future__ import annotations

from typing import List, Optional

import numpy as np

from ecgen_eval.metrics.base import BaseMetric, MetricResult

_DESCRIPTION = "One-line description shown in reports and list-metrics."
_REFERENCE = "Author, A. (2025). Title. Venue. https://doi.org/..."


class MyMetric(BaseMetric):
    name = "my_metric"
    description = _DESCRIPTION
    reference = _REFERENCE
    higher_is_better = False

    def __init__(self, n_subsample: int = 1000, seed: int = 42):
        self.n_subsample = n_subsample
        self.seed = seed

    def compute(
        self,
        real: np.ndarray,
        synth: np.ndarray,
        lead_names: Optional[List[str]] = None,
    ) -> MetricResult:
        self._check_inputs(real, synth)            # validates (N, L, T) and lead count
        n_leads = real.shape[1]
        if lead_names is None:
            lead_names = [f"L{i+1}" for i in range(n_leads)]

        per_lead: dict = {}
        for li, lname in enumerate(lead_names):
            r = real[:, li, :]
            s = synth[:, li, :]
            per_lead[lname] = float(abs(r.std() - s.std()))

        return MetricResult(
            metric_name=self.name,
            score=float(np.mean(list(per_lead.values()))),
            higher_is_better=self.higher_is_better,
            per_lead_scores=per_lead,
            description=self.description,
            reference=self.reference,
            extra={},
        )
```

Guidelines:

- Keep the constructor **callable without arguments** — the CLI and `list-metrics` do `cls()`.
- Use `n_subsample` and a fixed `seed` for anything random or quadratic in `N`.
- Put optional dependencies inside functions with an `ImportError` fallback.
- Put anything a plot might need (distributions, curves, sub-scores) in `extra`.

## 2. Register it

In `ecgen_eval/metrics/__init__.py`:

```python
from ecgen_eval.metrics.my_metric import MyMetric

AVAILABLE_METRICS = {
    ...
    "my_metric": MyMetric,
}
__all__ = [..., "MyMetric"]
```

The key becomes a valid value for `ecgen-eval eval -m my_metric`.

## 3. Test it

Add tests in `tests/test_metrics.py` using the `real_ecg` / `synth_ecg` fixtures from
`tests/conftest.py`:

```python
def test_my_metric(real_ecg, synth_ecg):
    from ecgen_eval.metrics import MyMetric
    result = MyMetric().compute(real_ecg, synth_ecg)
    assert np.isfinite(result.score)
    assert len(result.per_lead_scores) == real_ecg.shape[1]


def test_my_metric_identical_is_best(real_ecg):
    from ecgen_eval.metrics import MyMetric
    assert MyMetric().compute(real_ecg, real_ecg).score == pytest.approx(0.0, abs=1e-6)
```

```bash
pytest tests/test_metrics.py -v
```

## 4. Document it

- Add a row to the table in `docs/user-guide/metrics.md` and a section in
  `docs/user-guide/metric-reference.md`.
- Add the citation to `docs/references.md` and the README.
- The API reference picks up the class from its docstring automatically once it is listed in
  `docs/api/metrics.md`.
