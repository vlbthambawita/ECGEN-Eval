# Synthetic ECG signal generation using generative neural networks
- **ID / Year / Venue:** P140 / 2025 / PLoS ONE
- **Model & task:** Comparison of five GAN variants for normal-beat synthesis
- **Losses:** BCE adversarial; L1 + adversarial for AE/VAE-GAN hybrid; WGAN
- **Evaluation:** DTW/Frechet/Euclidean distances, set-average distance, template distances, productivity (acceptance) rate, expert visual check, augmentation F1
- **Data:** MIT-BIH, lead I normal beats, 256 samples
- **Takeaway for ECGEN-Eval:** Acceptance/productivity rate under a DTW threshold is a practical metric; avoid plain Euclidean for morphology.
- *Extraction source: full-text*
