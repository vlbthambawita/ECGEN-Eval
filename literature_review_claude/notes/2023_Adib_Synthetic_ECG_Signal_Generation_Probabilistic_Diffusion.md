# Synthetic ECG Signal Generation Using Probabilistic Diffusion Models
- **ID / Year / Venue:** P167 / 2023 / IEEE Access
- **Model & task:** Diffusion (Improved DDPM on 2D GASF/GADF/MTF image embeddings of beats) vs GAN (WGAN-GP); unconditional (Normal Sinus Beat only)
- **Losses:** Improved DDPM hybrid loss L_hybrid = L_simple + lambda L_vlb (cosine schedule); WGAN-GP (Wasserstein + gradient penalty)
- **Evaluation:** Average DTW distance; average Frechet distance (quality vs real reference rl-rl); MMD^2 (linear kernel, 7000 vs 7000; real-vs-real reference); authenticity test: ResNet34 N vs L classifier trained on imbalanced set augmented with synthetic beats, reporting accuracy, precision, recall, ROC AUC, average precision, PR-AUC
- **Data:** MIT-BIH Arrhythmia (MLII; N class for generation, L class for authenticity test); leads: 1 (MLII); fs: 360 (beats resampled to 256 samples); length: single heartbeat (adaptive window, 256 samples)
- **Takeaway for ECGEN-Eval:** Always report real-vs-real reference values (split-half) for each metric to calibrate what 'good' means.
- *Extraction source: full-text*
