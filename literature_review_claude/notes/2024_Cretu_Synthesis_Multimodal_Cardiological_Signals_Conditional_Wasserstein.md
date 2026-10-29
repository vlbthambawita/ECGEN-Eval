# Synthesis of Multimodal Cardiological Signals Using a Conditional Wasserstein Generative Adversarial Network
- **ID / Year / Venue:** P136 / 2024 / IEEE Access
- **Model & task:** GAN (MC-WGAN: conditional WGAN-GP, 1D U-Net generator, conv critic); class-conditional joint synthesis of ECG, arterial (ABP) and central venous (CVP) pressure beats
- **Losses:** conditional Wasserstein loss with gradient penalty (λ=10)
- **Evaluation:** RMSE, MAE, MSE, PRD, discrete curve Fréchet distance, DTW, MMD (each generated beat vs all real beats, averaged), per class and per signal; comparison with published MIT-BIH results [fidelity, distribution]
- **Data:** private Harefield ICU data (29 patients; ECG V1 + ABP + CVP; N/AF/AT/LBBB/paced) and MIT-BIH Arrhythmia lead II (AAMI N/A/V/R/L); leads: 1 ECG + 2 pressure channels; fs: 1000 (private) / 360 (MIT-BIH) Hz; length: 0.8 s beats
- **Notes:** MIT-BIH: RMSE 0.205, PRD 20.5, FD 0.225, DTW 1.355, MMD 0.0051; private ECG PRD 25.1, CVP PRD 48.3. Distances are mean-over-all-real rather than nearest-neighbour, cross-paper tables mix protocols, and inter-signal consistency (ECG-to-pressure timing) is never measured.
- **Takeaway for ECGEN-Eval:** For multimodal or multi-channel generation ECGEN-Eval should add a cross-channel coupling check (e.g. R-peak to pressure-upstroke delay distribution) and state clearly whether paired metrics use nearest-neighbour or all-pairs averaging, since the two give very different numbers.
- *Extraction source: full-text*
