# Disentangling Physiology from Fidelity: Latent-Guided Diffusion Models for Cross-Modal Cardiac Synthesis
- **ID / Year / Venue:** P052 / 2026 / IEEE International Conference on Acoustics Speech and Signal Processing
- **Model & task:** Hybrid 'Mamba-Diff-VAE': shared Mamba-VAE encoder produces latent z that, with metadata (rest/post-exercise), conditions a Mamba U-Net diffusion decoder via AdaLN; bidirectional ECG<->PCG translation
- **Losses:** epsilon-MSE diffusion loss + 0.05 x KL
- **Evaluation:** MSE; Pearson; HR MAE / R-peak MAE; QRS-S1 interval MAE; 1D FID (PhysioNet 2016 1D ResNet); inference time; latent t-SNE; qualitative control demo; 5 seeds [fidelity, distribution, clinical, efficiency, conditional]
- **Data:** EPHNOGRAM (69 subjects, 15,847 paired segments, subject-disjoint); leads: 1; fs: 1000 Hz; length: 10 s
- **Notes:** PCG->ECG MSE 0.112, Corr 0.821, R-peak MAE 1.35, FID 18.2 (SSSD-style baseline 0.173/0.738/2.19/29.8); ECG->PCG Corr 0.847, HR MAE 1.15 BPM, QRS-S1 MAE 12.4 ms. Removing the VAE (end-to-end) drops Corr to 0.815. FID for generated ECG uses a heart-sound feature extractor; healthy subjects only.
- **Takeaway for ECGEN-Eval:** For paired cross-modal translation, add R-peak timing MAE and heart-rate MAE between generated and ground-truth ECG to the clinical metrics, and warn when FID/FED is computed with an encoder trained on a different modality (here a PCG network) rather than an ECG backbone.
- *Extraction source: full-text*
