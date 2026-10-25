# ECG signal generation using feature disentanglement auto-encoder
- **ID / Year / Venue:** P058 / 2025 / Physiological Measurement
- **Model & task:** VAE/AE hybrid (Feature Disentanglement Auto-Encoder with VAE-generated patient-independent codes + discriminator + auxiliary classifiers); task: class-cond / augmentation
- **Losses:** contrastive loss for latent disentanglement + auxiliary classifier losses + adversarial (discriminator) loss + autoencoder reconstruction (details unknown, abstract only)
- **Evaluation:** heartbeat classification with FAKE-train/FAKE-test partitions (train on synthetic test on real and vice versa); classifier improvement via data augmentation (tags: utility-TSTR)
- **Data:** MIT-BIH Arrhythmia; Icentia11K; leads: unknown (abstract only); fs: unknown (abstract only) Hz; length: heartbeat-level s
- **Notes:** Generates by swapping latent codes or replacing patient-independent factors with VAE samples; aimed at rare classes. Evaluation framed as FAKE-train/FAKE-test (TSTR/TRTS) on MIT-BIH and Icentia11K.
- **Takeaway for ECGEN-Eval:** Report both TSTR and TRTS (FAKE-train/FAKE-test) for class-conditional models.
- *Extraction source: abstract-only*
