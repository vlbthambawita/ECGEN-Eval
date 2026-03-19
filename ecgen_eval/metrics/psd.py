"""
Power Spectral Density (PSD) divergence metric.

Compares the frequency-domain distribution of real vs. synthetic ECGs using
the Jensen-Shannon divergence between their mean normalised PSDs per lead.

Reference
---------
Welch, P. D. (1967). The use of fast Fourier transform for the estimation of
power spectra: A method based on time averaging over short, modified
periodograms. *IEEE Transactions on Audio and Electroacoustics*, 15(2), 70–73.
https://doi.org/10.1109/TAU.1967.1161901

Also applied in ECG evaluation in:
  Golany, T., & Radinsky, K. (2019). PGANs: Personalized generative adversarial
  networks for ECG synthesis to improve patient-specific deep ECG classification.
  *AAAI*, 33(01), 557–564. https://doi.org/10.1609/aaai.v33i01.3301557

Implementation notes
--------------------
1. Compute the power spectral density of each signal per lead using Welch's method
   (or plain FFT if scipy is not available).
2. Average the PSD across samples to get a mean PSD for the real and synthetic sets.
3. Normalise each mean PSD to a probability distribution (sum to 1).
4. Compute the Jensen–Shannon divergence between the two distributions.
5. Report per-lead JS divergence and mean across leads as the overall score.

Range: 0 (identical spectra) to log(2) ≈ 0.693 (maximally different). Lower = better.
"""

from __future__ import annotations

from typing import List, Optional

import numpy as np

from ecgen_eval.metrics.base import BaseMetric, MetricResult


_REFERENCE = (
    "Welch, P. D. (1967). The use of fast Fourier transform for the estimation of "
    "power spectra: A method based on time averaging over short, modified periodograms. "
    "IEEE Transactions on Audio and Electroacoustics, 15(2), 70–73. "
    "https://doi.org/10.1109/TAU.1967.1161901"
)

_DESCRIPTION = (
    "PSD Divergence: Jensen–Shannon divergence between the mean normalised power "
    "spectral densities of real and synthetic ECGs per lead (frequency domain similarity). "
    "Range: [0, ln 2]. Lower is better."
)


class PSDMetric(BaseMetric):
    """
    Jensen-Shannon divergence between mean normalised PSDs per lead.

    Parameters
    ----------
    fs : float
        Sampling frequency in Hz. Default: 500.
    nperseg : int, optional
        Welch segment length. Default: min(256, T).
    n_subsample : int
        Cap on samples used per set. Default: 1000.
    """

    name = "psd"
    description = _DESCRIPTION
    reference = _REFERENCE
    higher_is_better = False

    def __init__(
        self,
        fs: float = 500.0,
        nperseg: Optional[int] = None,
        n_subsample: int = 1000,
    ):
        self.fs = fs
        self.nperseg = nperseg
        self.n_subsample = n_subsample

    def compute(
        self,
        real: np.ndarray,
        synth: np.ndarray,
        lead_names: Optional[List[str]] = None,
    ) -> MetricResult:
        """
        Parameters
        ----------
        real  : (N_r, L, T)
        synth : (N_s, L, T)
        """
        self._check_inputs(real, synth)
        n_leads = real.shape[1]
        if lead_names is None:
            lead_names = [f"L{i+1}" for i in range(n_leads)]

        rng = np.random.default_rng(42)
        r = real if real.shape[0] <= self.n_subsample else real[
            rng.choice(real.shape[0], self.n_subsample, replace=False)]
        s = synth if synth.shape[0] <= self.n_subsample else synth[
            rng.choice(synth.shape[0], self.n_subsample, replace=False)]

        psd_fn = self._make_psd_fn(real.shape[-1])

        per_lead: dict = {}
        per_lead_psd_real: dict = {}
        per_lead_psd_synth: dict = {}

        for li, lname in enumerate(lead_names):
            psd_r = np.stack([psd_fn(r[i, li, :]) for i in range(r.shape[0])], axis=0)
            psd_s = np.stack([psd_fn(s[i, li, :]) for i in range(s.shape[0])], axis=0)

            mean_r = np.mean(psd_r, axis=0)
            mean_s = np.mean(psd_s, axis=0)

            jsd = self._js_divergence(mean_r, mean_s)
            per_lead[lname] = float(jsd)
            per_lead_psd_real[lname] = mean_r.tolist()
            per_lead_psd_synth[lname] = mean_s.tolist()

        overall = float(np.mean(list(per_lead.values())))

        return MetricResult(
            metric_name=self.name,
            score=overall,
            higher_is_better=self.higher_is_better,
            per_lead_scores=per_lead,
            description=self.description,
            reference=self.reference,
            extra={
                "per_lead_psd_real": per_lead_psd_real,
                "per_lead_psd_synth": per_lead_psd_synth,
            },
        )

    # ------------------------------------------------------------------ #

    def _make_psd_fn(self, n_timepoints: int):
        """Return a function that computes a normalised PSD for one signal."""
        nperseg = self.nperseg or min(256, n_timepoints)
        try:
            from scipy.signal import welch

            def psd_welch(x: np.ndarray) -> np.ndarray:
                _, pxx = welch(x.astype(np.float64), fs=self.fs, nperseg=nperseg)
                return (pxx + 1e-12) / (pxx.sum() + 1e-12)

            return psd_welch
        except ImportError:
            def psd_fft(x: np.ndarray) -> np.ndarray:
                n = len(x)
                fft_vals = np.abs(np.fft.rfft(x.astype(np.float64))) ** 2
                fft_vals = (fft_vals + 1e-12) / (fft_vals.sum() + 1e-12)
                return fft_vals

            return psd_fft

    @staticmethod
    def _js_divergence(p: np.ndarray, q: np.ndarray) -> float:
        """Jensen-Shannon divergence (base e). Range [0, ln 2]."""
        p = p / (p.sum() + 1e-12)
        q = q / (q.sum() + 1e-12)
        m = 0.5 * (p + q)
        kl_pm = np.sum(np.where(p > 0, p * np.log(p / (m + 1e-12)), 0.0))
        kl_qm = np.sum(np.where(q > 0, q * np.log(q / (m + 1e-12)), 0.0))
        return float(0.5 * kl_pm + 0.5 * kl_qm)
