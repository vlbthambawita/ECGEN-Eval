# Spatially-Conditioned Variational Autoencoder with Latent Manifold Harvesting for High-Fidelity 12-Lead ECG Synthesis
- **ID / Year / Venue:** P133 / 2026 / Research Square
- **Model & task:** SC-VAE: per-lead conditional VAE with spatial beat-position masks and harvested latent bank
- **Losses:** MSE + KL
- **Evaluation:** Visual inspection; classifier-predicted prevalence correlation and reliability score
- **Data:** Large 12-lead ECG DB (Chapman/Ningbo), 500 Hz, 10 s
- **Takeaway for ECGEN-Eval:** Classifier label-prevalence correlation and confidence are cheap conditional-fidelity checks; peak-alignment heuristics could serve as a plausibility metric.
- *Extraction source: full-text*
