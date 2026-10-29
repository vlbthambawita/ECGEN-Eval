# ECG waveform generation from radar signals: A deep learning perspective
- **ID / Year / Venue:** P154 / 2024 / Computers in Biology and Medicine
- **Model & task:** Deterministic 1D CNN regression (MultiResLinkNet vs FPN, UNet, LinkNet); radar→ECG translation
- **Losses:** MSE
- **Evaluation:** MAE; MSE; temporal and spectral correlation; temporal and spectral RRMSE; R-peak detection accuracy/precision/recall/F1; RR/HR/RMSSD agreement; qualitative plots [fidelity, clinical, conditional, robustness]
- **Data:** Schellenberger 24 GHz radar + ECG dataset (30 subjects; Resting/Valsalva/Apnea); leads: 1; fs: 128 Hz; length: 8 s (1024 samples)
- **Notes:** MultiResLinkNet temporal/spectral correlation 66.1/82.4 (Resting) and 61.9/80.0 (combined); R-peak F1 0.89-0.96; mean HR within ~1-2 bpm but RMSSD inflated ~2x, revealing beat-timing jitter. Point-wise metrics on [0,1]-normalised signals; 2026 corrigendum removed irrelevant citations only.
- **Takeaway for ECGEN-Eval:** For paired translation outputs, add paired R-peak detection F1 and HRV-difference (RMSSD/SDNN) checks, since HRV can be badly distorted even when mean HR and MAE look good.
- *Extraction source: full-text*
