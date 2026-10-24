# Adding a FED Backbone

`FEDMetric` is backbone-agnostic: it asks
[`get_encoder`](../api/encoders.md) for an object with an `encode` method and computes the
Fréchet distance between the returned embeddings. Adding a model therefore only touches
`ecgen_eval/metrics/encoders/`.

## 1. Write an adapter

Create `ecgen_eval/metrics/encoders/my_model.py`:

```python
"""
MyModel encoder adapter.

Model   : MyModel (architecture)
Source  : org/my-model on HuggingFace
Paper   : ...
"""

from __future__ import annotations

import numpy as np

_HF_REPO = "org/my-model"


class MyModelEncoder:
    """Lazy-loading encoder wrapper for MyModel."""

    def __init__(self, device: str = "cpu", batch_size: int = 32):
        self.device = device
        self.batch_size = batch_size
        self._model = None  # loaded lazily

    def _load_model(self):
        if self._model is not None:
            return
        try:
            import torch  # noqa: F401
            from huggingface_hub import hf_hub_download
        except ImportError as exc:
            raise ImportError(
                "MyModel requires torch and huggingface_hub. "
                "Install with: pip install ecgen-eval[fed]"
            ) from exc
        ckpt = hf_hub_download(_HF_REPO, "model.pt")
        ...  # build the model, load weights, .eval().to(self.device)

    def encode(self, signals: np.ndarray) -> np.ndarray:
        """(N, L, T) → (N, D)."""
        self._load_model()
        import torch

        out = []
        with torch.no_grad():
            for i in range(0, len(signals), self.batch_size):
                x = torch.as_tensor(signals[i : i + self.batch_size], dtype=torch.float32)
                h = self._model(x.to(self.device))          # (B, T', D)
                out.append(h.mean(dim=1).cpu().numpy())     # mean-pool over time
        return np.concatenate(out, axis=0)
```

Requirements:

- **Lazy loading** — no download at import or construction time.
- **Input** `(N, L, T)` NumPy array; **output** `(N, D)` NumPy array.
- Handle lead-count and sampling-rate mismatches inside the adapter (pad, select, resample).
- Raise an `ImportError` with an install hint if `torch` etc. are missing.

## 2. Register it

In `ecgen_eval/metrics/encoders/__init__.py`, extend `SUPPORTED_BACKBONES`, `BackboneName`
and `get_encoder`:

```python
SUPPORTED_BACKBONES = ("ecgfounder", "hubert_ecg", "ecgfm", "my_model")

    elif name == "my_model":
        from ecgen_eval.metrics.encoders.my_model import MyModelEncoder
        return MyModelEncoder(device=device, batch_size=batch_size)
```

Then add `"my_model"` to the `--backbone` `click.Choice` in `ecgen_eval/cli.py`.

## 3. Test without downloads

Tests should not download weights. Mock the model, or monkeypatch `get_encoder` to return a
stub whose `encode` returns random embeddings, and check the shape contract and that
`FEDMetric(backbone="my_model").compute(...)` returns a finite score.

## 4. Document it

Add the backbone to the table in `docs/user-guide/fed.md` and its citation to
`docs/references.md`.
