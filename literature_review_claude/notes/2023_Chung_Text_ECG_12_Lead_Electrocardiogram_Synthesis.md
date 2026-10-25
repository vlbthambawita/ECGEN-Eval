# Text-to-ECG: 12-Lead Electrocardiogram Synthesis Conditioned on Clinical Text Reports
- **ID / Year / Venue:** P174 / 2023 / IEEE International Conference on Acoustics Speech and Signal Processing
- **Model & task:** AR-Transformer (Auto-TTE: VQ-VAE tokenizer + autoregressive Transformer decoder + HiFi-GAN decoder); baselines DDPM-style diffusion on raw 12-lead, Tacotron 2 + Griffin-Lim / HiFi-GAN; text-cond (clinical text reports + age/sex patient-specific embedding)
- **Losses:** VQ-VAE: L2 reconstruction + codebook + commitment (stop-gradient) losses; Transformer: token cross-entropy; HiFi-GAN: LS-GAN adversarial (MSD+MPD) + L1 STFT spectrogram loss + L1 discriminator feature-matching loss (weights 1, 2, 45)
- **Evaluation:** AUROC of ResNet-34 multi-label classifier on samples generated from diagnosis prompts (6 classes); CLIP score (ECG-text contrastive encoder); FID using self-supervised ECG model pretrained on PhysioNet 2021 (64-d features); precision and recall (Kynkaanniemi et al.); cardiologist ranking (3 cardiologists, text-ECG alignment and realism, 100 samples); 10x bootstrap mean/std and t-tests
- **Data:** PTB-XL (21,833 text-ECG pairs); private Sejong General Hospital dataset (37,329 pairs); leads: 12; fs: 500; length: 10
- **Takeaway for ECGEN-Eval:** Adopt CLIP-style condition-alignment score and bootstrap CIs for FID/precision/recall; document the embedding model.
- *Extraction source: full-text*
