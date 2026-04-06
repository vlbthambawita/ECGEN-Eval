"""
HuBERT-ECG encoder adapter.

Model   : HuBERT-ECG (BASE variant, 93 M parameters)
Source  : Edoardo-BS/hubert-ecg-base on HuggingFace
          (Edoardo-BS/hubert-ecg-large also supported via ``variant`` param)
Paper   : medRxiv 2024.11.14.24317328 — "HuBERT-ECG: a foundation model for
          broad-scope ECG tasks"
Training: 9,100,000 12-lead ECGs, 164 cardiovascular conditions

HuBERT-ECG is a masked-prediction Transformer trained on ECG signals.
We mean-pool the last hidden states across the time dimension to obtain a
single fixed-size embedding vector per recording.

The model processes one lead at a time (shape: (B, T) float32).  For a
multi-lead recording we encode each lead independently and then average the
per-lead embeddings into one recording-level vector.

Weights are downloaded from HuggingFace on the first call to ``encode()``
and cached in the default HuggingFace cache directory.  Set ``HF_HOME`` to
override the cache location.

Input  : (N, L, T) — N recordings × L leads × T timepoints
Output : (N, D)    — one embedding vector per recording
"""

from __future__ import annotations

import numpy as np

_HF_REPO_BASE = "Edoardo-BS/hubert-ecg-base"
_HF_REPO_LARGE = "Edoardo-BS/hubert-ecg-large"


class HuBERTECGEncoder:
    """
    Lazy-loading encoder wrapper for HuBERT-ECG.

    The HuggingFace checkpoint is downloaded only when ``encode()`` is called
    for the first time.

    Parameters
    ----------
    device : str
        PyTorch device (``"cpu"`` or ``"cuda"``).
    batch_size : int
        Recordings per forward pass.
    variant : str
        ``"base"`` (default, 93 M params) or ``"large"`` (188 M params).
    preload : bool
        If ``True``, download and load the model immediately on construction.
    """

    def __init__(
        self,
        device: str = "cpu",
        batch_size: int = 32,
        variant: str = "base",
        preload: bool = False,
    ):
        self.device = device
        self.batch_size = batch_size
        self.variant = variant
        self._model = None
        self._processor = None

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
                "torch is required for HuBERT-ECG. "
                "Install with: pip install ecgen-eval[fed]"
            ) from exc

        N, L, T = signals.shape
        all_embeddings = []
        self._model.eval()

        with torch.no_grad():
            for start in range(0, N, self.batch_size):
                batch = signals[start : start + self.batch_size]  # (B, L, T)
                B = batch.shape[0]

                # Encode each lead independently → average across leads
                lead_embeddings = []
                for li in range(L):
                    lead_signal = batch[:, li, :]  # (B, T)
                    emb = self._encode_lead(lead_signal)  # (B, D)
                    lead_embeddings.append(emb)

                # Stack (L, B, D) → mean over leads → (B, D)
                import torch as _torch
                stacked = _torch.stack(lead_embeddings, dim=0)  # (L, B, D)
                recording_emb = stacked.mean(dim=0)             # (B, D)
                all_embeddings.append(recording_emb.cpu().numpy())

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
            from transformers import AutoModel, AutoFeatureExtractor
        except ImportError as exc:
            raise ImportError(
                "torch and transformers are required for HuBERT-ECG. "
                "Install with: pip install ecgen-eval[fed]"
            ) from exc

        repo = _HF_REPO_LARGE if self.variant == "large" else _HF_REPO_BASE
        print(f"[HuBERT-ECG] Loading {self.variant} model from HuggingFace ({repo}) …")

        self._model = AutoModel.from_pretrained(repo, trust_remote_code=True)
        self._model = self._model.to(self.device)
        self._model.eval()

        # Feature extractor / processor is optional; some HuBERT-ECG checkpoints
        # do not ship one — we handle both cases.
        try:
            self._processor = AutoFeatureExtractor.from_pretrained(
                repo, trust_remote_code=True
            )
        except Exception:
            self._processor = None

        print(f"[HuBERT-ECG] Model loaded.")

    def _encode_lead(self, lead_signal):
        """
        Encode a single-lead batch.

        Parameters
        ----------
        lead_signal : np.ndarray, shape (B, T)

        Returns
        -------
        torch.Tensor, shape (B, D)
        """
        import torch

        if self._processor is not None:
            inputs = self._processor(
                lead_signal.tolist(),
                return_tensors="pt",
                sampling_rate=500,  # standard ECG sampling rate
                padding=True,
            )
            input_values = inputs["input_values"].to(self.device)
        else:
            input_values = torch.tensor(
                lead_signal, dtype=torch.float32
            ).to(self.device)  # (B, T)

        out = self._model(input_values, output_hidden_states=True)

        # Mean-pool the last hidden state over the time dimension → (B, D)
        if hasattr(out, "last_hidden_state"):
            hidden = out.last_hidden_state  # (B, T', D)
        else:
            hidden = out[0]

        emb = hidden.mean(dim=1)  # (B, D)
        return emb
