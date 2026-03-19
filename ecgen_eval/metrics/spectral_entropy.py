"""
Spectral Entropy Divergence for ECG evaluation.

Reference
---------
Inouye, T., Shinosaki, K., Sakamoto, H., Toi, S., Ukai, S., Iyama, A.,
Katsuda, Y., & Hirano, M. (1991).
Quantification of EEG irregularity by use of the entropy of the power
spectrum.
*Electroencephalography and Clinical Neurophysiology*, 79(3), 204–210.
https://doi.org/10.1016/0013-4694(91)90138-T

Applied to ECG and biomedical signal evaluation in:
Manis, G., Aktaruzzaman, M., & Sassi, R. (2017).
Bubble entropy: an entropy almost free of parameters.
*IEEE Transactions on Biomedical Engineering*, 64(11), 2711–2718.
https://doi.org/10.1109/TBME.2017.2664105

Implementation notes
--------------------
For each ECG recording the power spectral density is computed (Welch's
method via scipy if available, else plain FFT).  The normalised PSD is
treated as a probability distribution and Shannon entropy is computed:

  SE = -Σ p(f) · log₂ p(f)   (bits)

The score is the Jensen-Shannon (JS) divergence between the distributions
of spectral entropy values across real and synthetic ECGs (lower = more
similar distributional structure).

Range: [0, log(2) ≈ 0.693] nats.
"""

from __future__ import annotations

from typing import List, Optional

import numpy as np

from ecgen_eval.metrics.base import BaseMetric, MetricResult


_REFERENCE = (
    "Inouye, T., et al. (1991). Quantification of EEG irregularity by use of the entropy of "
    "the power spectrum. Electroencephalography and Clinical Neurophysiology, 79(3), 204–210. "
    "https://doi.org/10.1016/0013-4694(91)90138-T"
)

_DESCRIPTION = (
    "Spectral Entropy Divergence: JS divergence between real and synthetic distributions of "
    "per-recording spectral entropy (bits). Lower is better (0 = identical distributions)."
)


class SpectralEntropyMetric(BaseMetric):
    """
    Spectral entropy distribution comparison per lead.

    Parameters
    ----------
    fs : float
        Sampling frequency in Hz. Default: 500.
    nperseg : int or None
        Welch segment length. None → min(256, T). Default: None.
    n_subsample : int
        Max samples per lead. Default: 1000.
    seed : int
        Random seed. Default: 42.
    """

    name = "spectral_entropy"
    description = _DESCRIPTION
    reference = _REFERENCE
    higher_is_better = False

    def __init__(
        self,
        fs: float = 500.0,
        nperseg: Optional[int] = None,
        n_subsample: int = 1000,
        seed: int = 42,
    ):
        self.fs = fs
        self.nperseg = nperseg
        self.n_subsample = n_subsample
        self.seed = seed

    def compute(
        self,
        real: np.ndarray,
        synth: np.ndarray,
        lead_names: Optional[List[str]] = None,
    ) -> MetricResult:
        self._check_inputs(real, synth)
        n_leads = real.shape[1]
        T = real.shape[2]
        if lead_names is None:
            lead_names = [f"L{i+1}" for i in range(n_leads)]

        nperseg = self.nperseg or min(256, T)
        rng = np.random.default_rng(self.seed)
        per_lead: dict = {}
        extra: dict = {}

        for li, lname in enumerate(lead_names):
            real_l = real[:, li, :]    # (Nr, T)
            synth_l = synth[:, li, :]  # (Ns, T)

            real_l = self._subsample(real_l, rng)
            synth_l = self._subsample(synth_l, rng)

            se_r = self._batch_spectral_entropy(real_l, nperseg)   # (Nr,)
            se_s = self._batch_spectral_entropy(synth_l, nperseg)  # (Ns,)

            js = self._js_divergence(se_r, se_s)
            per_lead[lname] = float(js)
            extra[lname] = {
                "real_se_mean": float(np.mean(se_r)),
                "real_se_std": float(np.std(se_r)),
                "synth_se_mean": float(np.mean(se_s)),
                "synth_se_std": float(np.std(se_s)),
            }

        score = float(np.mean(list(per_lead.values())))
        return MetricResult(
            metric_name=self.name,
            score=score,
            higher_is_better=self.higher_is_better,
            per_lead_scores=per_lead,
            description=self.description,
            reference=self.reference,
            extra=extra,
        )

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _batch_spectral_entropy(self, signals: np.ndarray, nperseg: int) -> np.ndarray:
        """Compute spectral entropy (bits) per recording."""
        se_vals = []
        for sig in signals:
            psd = self._compute_psd(sig, nperseg)
            psd = psd + 1e-15
            psd /= psd.sum()
            se = float(-np.sum(psd * np.log2(psd)))
            se_vals.append(se)
        return np.array(se_vals, dtype=np.float32)

    def _compute_psd(self, signal: np.ndarray, nperseg: int) -> np.ndarray:
        try:
            from scipy.signal import welch
            _, psd = welch(signal, fs=self.fs, nperseg=nperseg)
            return psd
        except ImportError:
            pass
        # Plain FFT fallback
        fft = np.fft.rfft(signal)
        psd = (np.abs(fft) ** 2) / len(signal)
        return psd

    @staticmethod
    def _js_divergence(p_vals: np.ndarray, q_vals: np.ndarray, n_bins: int = 50) -> float:
        lo = min(p_vals.min(), q_vals.min())
        hi = max(p_vals.max(), q_vals.max())
        if hi <= lo:
            return 0.0
        bins = np.linspace(lo, hi, n_bins + 1)
        p_hist, _ = np.histogram(p_vals, bins=bins, density=True)
        q_hist, _ = np.histogram(q_vals, bins=bins, density=True)
        p_hist = p_hist + 1e-10
        q_hist = q_hist + 1e-10
        p_hist /= p_hist.sum()
        q_hist /= q_hist.sum()
        m = 0.5 * (p_hist + q_hist)
        eps = 1e-15
        js = 0.5 * (
            np.sum(p_hist * np.log((p_hist + eps) / (m + eps)))
            + np.sum(q_hist * np.log((q_hist + eps) / (m + eps)))
        )
        return float(np.clip(js, 0.0, np.log(2)))

    def _subsample(self, X: np.ndarray, rng: np.random.Generator) -> np.ndarray:
        if X.shape[0] <= self.n_subsample:
            return X
        idx = rng.choice(X.shape[0], size=self.n_subsample, replace=False)
        return X[idx]
