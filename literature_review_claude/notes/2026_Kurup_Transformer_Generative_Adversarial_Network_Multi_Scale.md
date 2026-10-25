# Transformer-Based Generative Adversarial Network With Multi-Scale Temporal Attention for ECG Synthesis and PQRST Feature Preservation
- **ID / Year / Venue:** P147 / 2026 / IEEE Access
- **Model & task:** GAN (TransGAN: Transformer generator with temporal self-attention, hierarchical multi-scale patch discriminator, PQRST-constrained module); augmentation (class-imbalanced synthesis)
- **Losses:** adversarial (multi-scale patch discriminator) + weighted Binary Cross-Entropy (WBCE) for imbalance + PQRST feature constraint
- **Evaluation:** MSE; DTW distance; Wasserstein distance (WD); PQRST feature accuracy; downstream classification accuracy
- **Data:** unknown (abstract only); leads: unknown (abstract only); fs: unknown (abstract only); length: unknown (abstract only)
- **Takeaway for ECGEN-Eval:** PQRST feature accuracy (fiducial-point agreement) is a clinical metric worth adding next to DTW/WD.
- *Extraction source: abstract-only*
