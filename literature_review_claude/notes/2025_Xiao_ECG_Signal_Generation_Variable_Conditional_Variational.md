# ECG Signal Generation Using Variable β-Conditional Variational Autoencoder
- **ID / Year / Venue:** P059 / 2025 / IEEE EMBC 2025
- **Model & task:** VAE (conditional β-VAE, FC or 1D-CNN, 8-d latent, annealed β); class-conditional beat synthesis (N, LBBB, RBBB, PVC) with RR-based stitching into 5 s strips for augmentation
- **Losses:** MSE reconstruction + β-weighted KL (KL annealing)
- **Evaluation:** SVM FAKE-test ('fidelity %') and FAKE-train ('diversity %'); PCA plots; augmentation accuracy on CPSC 2018 [fidelity, diversity, utility-TSTR]
- **Data:** MIT-BIH Arrhythmia (lead II, 4,000 beats/class) and CPSC 2018 (lead II, resampled); leads: 1; fs: 360 Hz; length: 0.71 s beats (256 samples), 5 s stitched strips
- **Notes:** Best fidelity 94.13% / diversity 93.71% (CNN, β=0.5); configuration changes shift scores by only ~1-2 pts. Augmentation raised accuracy from 66.85% to at most 70.61% and degraded with more synthetic data. No distribution metrics or GAN baseline; authors acknowledge the lack of consensus metrics.
- **Takeaway for ECGEN-Eval:** Classifier-based fidelity/diversity scores barely discriminate between model variants; ECGEN-Eval should complement them with distributional metrics (mmd, fd, pr_dist) and a per-class report when evaluating class-conditional beat generators.
- *Extraction source: full-text*
