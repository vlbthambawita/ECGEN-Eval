"""
ECG foundation-model encoder adapters for Fréchet ECG Distance (FED).

Each adapter exposes a single ``encode(signals)`` method:

    signals : np.ndarray, shape (N, L, T)
        N recordings × L leads × T timepoints.

    returns : np.ndarray, shape (N, D)
        One embedding vector per recording.

Weights are downloaded from HuggingFace on first use and cached in the
default HuggingFace cache directory (~/.cache/huggingface).
Set the ``HF_HOME`` environment variable to change the cache location.

Supported backbone names
------------------------
- ``"ecgfounder"``  — ECGFounder (PKUDigitalHealth/ECGFounder, RegNet, 10.7 M ECGs)
- ``"hubert_ecg"``  — HuBERT-ECG (Edoardo-BS/hubert-ecg-base, Transformer, 9.1 M ECGs)
- ``"ecgfm"``       — ECG-FM (bowang-lab/ECG-FM, wav2vec2-style, 1.5 M ECGs)
"""

from __future__ import annotations

from typing import Literal

SUPPORTED_BACKBONES = ("ecgfounder", "hubert_ecg", "ecgfm")
BackboneName = Literal["ecgfounder", "hubert_ecg", "ecgfm"]


def get_encoder(name: str, device: str = "cpu", batch_size: int = 32):
    """
    Return an initialised encoder adapter for the requested backbone.

    Parameters
    ----------
    name : str
        One of ``"ecgfounder"``, ``"hubert_ecg"``, ``"ecgfm"``.
    device : str
        PyTorch device string, e.g. ``"cpu"`` or ``"cuda"``.
    batch_size : int
        Number of recordings to process per forward pass.

    Returns
    -------
    An encoder object with an ``encode(signals: np.ndarray) -> np.ndarray`` method.

    Raises
    ------
    ValueError
        If *name* is not a recognised backbone.
    ImportError
        If ``torch`` / ``transformers`` are not installed.
    """
    if name == "ecgfounder":
        from ecgen_eval.metrics.encoders.ecgfounder import ECGFounderEncoder
        return ECGFounderEncoder(device=device, batch_size=batch_size)
    elif name == "hubert_ecg":
        from ecgen_eval.metrics.encoders.hubert_ecg import HuBERTECGEncoder
        return HuBERTECGEncoder(device=device, batch_size=batch_size)
    elif name == "ecgfm":
        from ecgen_eval.metrics.encoders.ecgfm import ECGFMEncoder
        return ECGFMEncoder(device=device, batch_size=batch_size)
    else:
        raise ValueError(
            f"Unknown backbone '{name}'. Supported: {SUPPORTED_BACKBONES}"
        )
