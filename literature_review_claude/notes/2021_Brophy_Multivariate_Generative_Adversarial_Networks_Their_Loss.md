# Multivariate Generative Adversarial Networks and Their Loss Functions for Synthesis of Multichannel ECGs
- **ID / Year / Venue:** P173 / 2021 / IEEE Access
- **Model & task:** GAN (MVGAN: 2-layer LSTM generator, 2-D CNN discriminator with minibatch discrimination; DP variant); task: unconditional
- **Losses:** Compared losses: LSGAN; LSGAN-DTW (LSGAN with multivariate DTW penalty term); DTWGAN (MVDTW as criterion); Loss-Sensitive GAN (LS-GAN); LS-GAN-DTW; DP via gradient noise (GAN-DP)
- **Evaluation:** MMD; multivariate dependent DTW (MVDTW); real-vs-synthetic discriminability by SVC and LSTM classifiers (accuracy near 0.5 = good); membership inference attack (presence disclosure precision/recall vs threshold ε); benchmarks vs multivariate VAE and LSTM (tags: distribution; fidelity; privacy)
- **Data:** MIT-BIH Normal Sinus Rhythm; MIT-BIH Arrhythmia; leads: 2; fs: 100 (resampled from 128/360) Hz; length: 5 (500 samples) s
- **Notes:** LSGAN-DTW best (4.9% over LSGAN on normalised MMD+DTW). MIA: ~0% recall for ε ≤0.4·mean distance; DP version 0% up to 0.5. Early use of classifier two-sample test and MIA for ECG GANs.
- **Takeaway for ECGEN-Eval:** Add classifier two-sample test (real-vs-synthetic discriminability) and distance-threshold membership inference to the privacy section.
- *Extraction source: full-text*
