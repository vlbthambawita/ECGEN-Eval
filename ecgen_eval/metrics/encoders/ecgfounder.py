"""
ECGFounder encoder adapter.

Model   : ECGFounder (RegNet-based CNN)
Source  : PKUDigitalHealth/ECGFounder on HuggingFace
Paper   : arXiv 2410.04133 — "ECGFounder: An ECG Foundation Model Built on
          over 10 Million Recordings with Expert Annotations" (NEJM AI, 2025)
Training: 10,771,552 ECGs, 150 diagnostic categories

Weights are downloaded from HuggingFace on the first call to ``encode()``
and cached in the default HuggingFace cache directory.  Set ``HF_HOME`` to
override the cache location.

Input  : (N, L, T) — N recordings × L leads × T timepoints
Output : (N, D)    — one embedding vector per recording
"""

from __future__ import annotations

from typing import Optional

import numpy as np

_HF_REPO = "PKUDigitalHealth/ECGFounder"

# ECGFounder expects 12-lead input; if fewer leads are provided we repeat the
# last lead to pad up to 12.
_EXPECTED_LEADS = 12


class ECGFounderEncoder:
    """
    Lazy-loading encoder wrapper for ECGFounder.

    The HuggingFace checkpoint is downloaded only when ``encode()`` is called
    for the first time (or when the object is first constructed if
    ``preload=True``).

    Parameters
    ----------
    device : str
        PyTorch device (``"cpu"`` or ``"cuda"``).
    batch_size : int
        Recordings per forward pass.
    preload : bool
        If ``True``, download and load the model immediately on construction.
    """

    def __init__(self, device: str = "cpu", batch_size: int = 32, preload: bool = False):
        self.device = device
        self.batch_size = batch_size
        self._model = None  # loaded lazily

        if preload:
            self._load_model()

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def encode(self, signals: np.ndarray) -> np.ndarray:
        """
        Encode ECG signals into embedding vectors.

        Parameters
        ----------
        signals : np.ndarray, shape (N, L, T)

        Returns
        -------
        np.ndarray, shape (N, D)
        """
        self._load_model()  # no-op if already loaded

        try:
            import torch
        except ImportError as exc:
            raise ImportError(
                "torch is required for ECGFounder. "
                "Install with: pip install ecgen-eval[fed]"
            ) from exc

        N, L, T = signals.shape
        signals = self._pad_leads(signals)  # → (N, 12, T)

        all_embeddings = []
        self._model.eval()

        with torch.no_grad():
            for start in range(0, N, self.batch_size):
                batch = signals[start : start + self.batch_size]
                x = torch.tensor(batch, dtype=torch.float32).to(self.device)
                emb = self._forward(x)  # (B, D)
                all_embeddings.append(emb.cpu().numpy())

        return np.concatenate(all_embeddings, axis=0)

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _load_model(self):
        """Download and cache the model on first use."""
        if self._model is not None:
            return

        try:
            import torch
            from transformers import AutoModel
        except ImportError as exc:
            raise ImportError(
                "torch and transformers are required for ECGFounder. "
                "Install with: pip install ecgen-eval[fed]"
            ) from exc

        print(f"[ECGFounder] Loading model from HuggingFace ({_HF_REPO}) …")
        self._model = AutoModel.from_pretrained(_HF_REPO, trust_remote_code=True)
        self._model = self._model.to(self.device)
        self._model.eval()
        print("[ECGFounder] Model loaded.")

    def _forward(self, x):
        """
        Run a batch through ECGFounder and return pooled embeddings.

        ECGFounder is a RegNet CNN.  We call the model's forward pass and
        extract the feature representation before the classification head via
        the ``output_hidden_states`` flag or by hooking the backbone directly.
        If the model exposes a ``get_features`` / ``forward_features`` method
        we use that; otherwise we fall back to global-average-pooling the last
        hidden state.
        """
        import torch

        # Prefer an explicit feature-extraction entry point if available.
        if hasattr(self._model, "forward_features"):
            feats = self._model.forward_features(x)
        elif hasattr(self._model, "get_features"):
            feats = self._model.get_features(x)
        else:
            out = self._model(x, output_hidden_states=True)
            # Use the last hidden state; global-average-pool over time/space.
            hidden = out.hidden_states[-1] if hasattr(out, "hidden_states") else out[0]
            feats = hidden

        # Global average pool if more than 2 dims remain after forward pass.
        if feats.dim() > 2:
            feats = feats.mean(dim=list(range(2, feats.dim())))

        return feats  # (B, D)

    @staticmethod
    def _pad_leads(signals: np.ndarray) -> np.ndarray:
        """Pad or truncate to exactly ``_EXPECTED_LEADS`` leads."""
        N, L, T = signals.shape
        if L == _EXPECTED_LEADS:
            return signals
        if L > _EXPECTED_LEADS:
            return signals[:, :_EXPECTED_LEADS, :]
        # Repeat the last lead to fill up to 12
        pad = np.repeat(signals[:, -1:, :], _EXPECTED_LEADS - L, axis=1)
        return np.concatenate([signals, pad], axis=1)
