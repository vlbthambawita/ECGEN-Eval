"""
Fréchet ECG Distance (FED) metric.

Computes the Fréchet Distance between the multivariate Gaussian distributions
fitted to deep embeddings extracted from real and synthetic ECG recordings
using a pre-trained ECG foundation model.

This is the ECG analogue of:
  - FID  (image generation) — Heusel et al., NeurIPS 2017
  - FAD  (audio generation) — Kilgour et al., Interspeech 2018

Unlike the handcrafted-feature ``FDMetric`` (``fd.py``), FED uses a
foundation model's learned representations, which capture richer clinical
and morphological structure.

Supported backbone models
--------------------------
ecgfounder
    ECGFounder — RegNet CNN trained on 10.7 M ECGs (PKU Digital Health / NEJM AI 2025).
    arXiv: 2410.04133  HuggingFace: PKUDigitalHealth/ECGFounder
hubert_ecg
    HuBERT-ECG — HuBERT-style Transformer trained on 9.1 M ECGs (medRxiv 2024).
    arXiv: 2024.11.14.24317328  HuggingFace: Edoardo-BS/hubert-ecg-base
ecgfm
    ECG-FM — wav2vec 2.0-style model trained on 1.5 M ECGs (JAMIA Open 2025).
    arXiv: 2408.05178  HuggingFace: bowang-lab/ECG-FM

Lazy checkpoint download
-------------------------
Model weights are downloaded from HuggingFace **on the first call to
``compute()``** (or when ``encode()`` is called on the encoder).  Nothing is
downloaded at import time or at ``FEDMetric`` construction time.  Downloaded
weights are cached in the HuggingFace local cache directory.  Set the
``HF_HOME`` environment variable to change the cache location.

FD formula
----------
FED = ‖μ_r − μ_s‖² + Tr(Σ_r + Σ_s − 2·(Σ_r Σ_s)^½)

where μ and Σ are estimated from the (N, D) embedding matrices of the real
and synthetic sets respectively.

Lower is better; 0 means the two distributions are identical.
"""

from __future__ import annotations

from typing import List, Optional

import numpy as np

from ecgen_eval.metrics.base import BaseMetric, MetricResult
from ecgen_eval.metrics._frechet_utils import frechet_distance

_REFERENCE = (
    "Heusel, M., et al. (2017). GANs trained by a two time-scale update rule. NeurIPS, 30. "
    "https://arxiv.org/abs/1706.08500 | "
    "ECGFounder: arXiv 2410.04133 | "
    "HuBERT-ECG: medRxiv 2024.11.14.24317328 | "
    "ECG-FM: arXiv 2408.05178"
)

_DESCRIPTION = (
    "Fréchet ECG Distance (FED): measures the distance between multivariate Gaussians "
    "fitted to deep embeddings (from a pre-trained ECG foundation model) of real and "
    "synthetic ECG sets. Analogous to FID for images. Lower is better."
)


class FEDMetric(BaseMetric):
    """
    Fréchet ECG Distance using deep foundation-model embeddings.

    Parameters
    ----------
    backbone : str
        Which foundation model to use as the feature extractor.
        One of ``"ecgfounder"`` (default), ``"hubert_ecg"``, ``"ecgfm"``.
    device : str
        PyTorch device string, e.g. ``"cpu"`` or ``"cuda"``.
    batch_size : int
        Number of recordings per encoder forward pass.
    n_subsample : int or None
        If set, randomly subsample at most this many recordings from each set
        before computing embeddings (useful for large datasets).  Default: ``None``
        (use all recordings).
    eps : float
        Regularisation term added to covariance diagonal for numerical stability.

    Notes
    -----
    Model weights are downloaded from HuggingFace on the **first call to
    ``compute()``**.  Set the ``HF_HOME`` environment variable to control
    the cache directory.
    """

    name = "fed"
    description = _DESCRIPTION
    reference = _REFERENCE
    higher_is_better = False

    def __init__(
        self,
        backbone: str = "ecgfounder",
        device: str = "cpu",
        batch_size: int = 32,
        n_subsample: Optional[int] = None,
        eps: float = 1e-6,
    ):
        self.backbone = backbone
        self.device = device
        self.batch_size = batch_size
        self.n_subsample = n_subsample
        self.eps = eps
        self._encoder = None  # loaded lazily on first compute()

    # ------------------------------------------------------------------ #
    # BaseMetric interface                                                 #
    # ------------------------------------------------------------------ #

    def compute(
        self,
        real: np.ndarray,
        synth: np.ndarray,
        lead_names: Optional[List[str]] = None,
    ) -> MetricResult:
        """
        Compute the Fréchet ECG Distance between *real* and *synth*.

        Parameters
        ----------
        real : np.ndarray, shape (N, L, T)
        synth : np.ndarray, shape (M, L, T)
        lead_names : list[str] or None
            Ignored for FED (embeddings are global, not per-lead).

        Returns
        -------
        MetricResult
            ``score`` is the scalar FED value.  ``per_lead_scores`` is empty
            because FED operates on whole-recording embeddings.
        """
        self._check_inputs(real, synth)

        # Lazy-load encoder (downloads weights on first call)
        if self._encoder is None:
            from ecgen_eval.metrics.encoders import get_encoder
            self._encoder = get_encoder(
                self.backbone, device=self.device, batch_size=self.batch_size
            )

        # Optional subsampling
        rng = np.random.default_rng(42)
        r = self._maybe_subsample(real, rng)
        s = self._maybe_subsample(synth, rng)

        # Extract embeddings: (N, D) and (M, D)
        emb_real = self._encoder.encode(r)
        emb_synth = self._encoder.encode(s)

        score = frechet_distance(emb_real, emb_synth, eps=self.eps)

        return MetricResult(
            metric_name=self.name,
            score=float(score),
            higher_is_better=self.higher_is_better,
            per_lead_scores={},
            description=self.description,
            reference=self.reference,
            extra={"backbone": self.backbone},
        )

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _maybe_subsample(self, arr: np.ndarray, rng) -> np.ndarray:
        if self.n_subsample is None or arr.shape[0] <= self.n_subsample:
            return arr
        idx = rng.choice(arr.shape[0], self.n_subsample, replace=False)
        return arr[idx]
