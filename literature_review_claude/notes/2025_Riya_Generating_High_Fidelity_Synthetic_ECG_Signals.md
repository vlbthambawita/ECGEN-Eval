# Generating High-Fidelity Synthetic ECG Signals Using Deep Autoencoder Architectures
- **ID / Year / Venue:** P078 / 2025 / not reported
- **Model & task:** VAE / Autoencoders (LSTM-AE, CNN-AE, VAE, Denoising AE); unconditional (reconstruction-based synthesis)
- **Losses:** MSE reconstruction (VAE KL presumably; not stated in abstract)
- **Evaluation:** training MSE; Pearson correlation coefficient; SNR (dB) [fidelity]
- **Data:** unknown (abstract only); leads: unknown (abstract only); fs: unknown (abstract only) Hz; length: unknown (abstract only) s
- **Notes:** CNNAE PCC 0.999966, SNR 51.18 dB: reconstruction metrics only, which reward near-identity copying and say nothing about generative diversity or distribution match.
- **Takeaway for ECGEN-Eval:** Pitfall example: reconstruction PCC/SNR is not generative quality; pair with distribution and memorisation metrics.
- *Extraction source: abstract-only*
