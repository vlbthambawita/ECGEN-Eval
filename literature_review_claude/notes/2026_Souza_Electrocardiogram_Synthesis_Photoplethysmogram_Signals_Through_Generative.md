# Electrocardiogram Synthesis from Photoplethysmogram Signals Through Generative Adversarial Networks
- **ID / Year / Venue:** P068 / 2026 / IEEE Latin American Symposium on Circuits and Systems (LASCAS)
- **Model & task:** GAN (dual-domain discriminators: time and frequency); task: PPG2ECG
- **Losses:** adversarial loss with time-domain and frequency-domain discriminators (other terms unknown)
- **Evaluation:** MSE; Pearson correlation coefficient; similarity % from normalized MSE (tags: fidelity)
- **Data:** public PPG-ECG datasets + custom synchronized hardware recordings; leads: unknown (abstract only); fs: unknown (abstract only) Hz; length: unknown (abstract only) s
- **Notes:** MSE 0.2780±0.05, ρ=0.68±0.03, 72.2% similarity (normalized MSE) under varying HR/activity/noise. Includes preprocessing for narrowband/broadband noise.
- **Takeaway for ECGEN-Eval:** Frequency-domain discriminator idea mirrors a spectral fidelity metric (PSD distance) worth reporting.
- *Extraction source: abstract-only*
