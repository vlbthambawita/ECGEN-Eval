"""
ECG-FM encoder adapter.

Model   : ECG-FM (Electrocardiogram Foundation Model)
Source  : bowang-lab/ECG-FM on HuggingFace
Paper   : arXiv 2408.05178 — "ECG-FM: An Open Electrocardiogram Foundation
          Model" (JAMIA Open, 2025)
Training: 1,500,000 12-lead ECGs from MIMIC-IV-ECG; hybrid contrastive
          (CMSC/CLOCS) + masked reconstruction (RLM) objectives.
          Architecture: 1-D convolutional feature encoder feeding a
          Transformer context encoder (wav2vec 2.0-style).

We run the full encoder and mean-pool the context encoder's output over
the time dimension to obtain a single fixed-size embedding per recording.
The paper validates this embedding as "a robust, competitive feature-set
generator" for downstream tasks.

Weights are downloaded from HuggingFace on the first call to ``encode()``
and cached in the default HuggingFace cache directory.  Set ``HF_HOME`` to
override the cache location.

Input  : (N, L, T) — N recordings × L leads × T timepoints
Output : (N, D)    — one embedding vector per recording
"""

from __future__ import annotations

import numpy as np

_HF_REPO = "bowang-lab/ECG-FM"

# ECG-FM expects 12-lead input at 500 Hz.
_EXPECTED_LEADS = 12


class ECGFMEncoder:
    """
    Lazy-loading encoder wrapper for ECG-FM.

    The HuggingFace checkpoint is downloaded only when ``encode()`` is called
    for the first time.

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
        self._model = None

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
        self._load_model()

        try:
            import torch
        except ImportError as exc:
            raise ImportError(
                "torch is required for ECG-FM. "
                "Install with: pip install ecgen-eval[fed]"
            ) from exc

        N, L, T = signals.shape
        signals = self._pad_leads(signals)  # → (N, 12, T)

        all_embeddings = []
        self._model.eval()

        with torch.no_grad():
            for start in range(0, N, self.batch_size):
                batch = signals[start : start + self.batch_size]  # (B, 12, T)
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
            import torch  # noqa: F401
            from transformers import AutoModel
        except ImportError as exc:
            raise ImportError(
                "torch and transformers are required for ECG-FM. "
                "Install with: pip install ecgen-eval[fed]"
            ) from exc

        print(f"[ECG-FM] Loading model from HuggingFace ({_HF_REPO}) …")
        self._model = AutoModel.from_pretrained(_HF_REPO, trust_remote_code=True)
        self._model = self._model.to(self.device)
        self._model.eval()
        print("[ECG-FM] Model loaded.")

    def _forward(self, x):
        """
        Run a batch through ECG-FM and return pooled embeddings.

        ECG-FM is wav2vec 2.0-style: a 1-D conv feature encoder feeds a
        Transformer context encoder.  We extract the context encoder's
        last hidden state and mean-pool over the time dimension.
        """
        out = self._model(x, output_hidden_states=True)

        if hasattr(out, "last_hidden_state"):
            # Standard HuggingFace output: (B, T', D)
            hidden = out.last_hidden_state
        elif hasattr(out, "hidden_states") and out.hidden_states is not None:
            hidden = out.hidden_states[-1]
        else:
            # Fallback: first element of whatever is returned
            hidden = out[0]

        # Mean-pool over time → (B, D)
        if hidden.dim() == 3:
            emb = hidden.mean(dim=1)
        else:
            emb = hidden  # already (B, D)

        return emb

    @staticmethod
    def _pad_leads(signals: np.ndarray) -> np.ndarray:
        """Pad or truncate to exactly ``_EXPECTED_LEADS`` leads."""
        N, L, T = signals.shape
        if L == _EXPECTED_LEADS:
            return signals
        if L > _EXPECTED_LEADS:
            return signals[:, :_EXPECTED_LEADS, :]
        pad = np.repeat(signals[:, -1:, :], _EXPECTED_LEADS - L, axis=1)
        return np.concatenate([signals, pad], axis=1)
