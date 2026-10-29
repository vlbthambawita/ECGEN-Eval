# Generating High-Fidelity Synthetic ECG Signals Using Deep Autoencoder Architectures
- **ID / Year / Venue:** P078 / 2025 / Artificial Intelligence and Smart Technologies for Sustainability Conference (AISTS)
- **Model & task:** Comparison of LSTM-AE, CNN-AE, VAE and denoising AE trained to reconstruct MIT-BIH ECG segments; reconstruction presented as 'synthetic ECG generation'
- **Losses:** MSE reconstruction; KL for VAE; denoising objective for DAE
- **Evaluation:** final MSE loss; Pearson correlation; SNR; training time; RR-interval agreement for CNN-AE; qualitative overlays [fidelity, clinical, efficiency]
- **Data:** MIT-BIH Arrhythmia (record 101 shown); leads: 1 (implied); fs: 360 Hz; length: not reported s
- **Notes:** CNN-AE PCC 0.999966, SNR 51.18 dB; VAE 0.9935 / 28.56 dB; RR intervals r = 1.000. Every metric is a paired input-vs-reconstruction comparison, so near-identity copying scores best; no sampling from the latent space, no distribution, diversity, memorisation or utility tests, no held-out evaluation described.
- **Takeaway for ECGEN-Eval:** A cautionary example: ECGEN-Eval should flag near-perfect paired scores (PCC near 1, SNR > 40 dB) together with nn_dist authenticity, because reconstruction fidelity without novelty indicates copying rather than generation.
- *Extraction source: full-text*
