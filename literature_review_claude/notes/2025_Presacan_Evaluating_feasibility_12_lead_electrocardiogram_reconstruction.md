# Evaluating the feasibility of 12-lead electrocardiogram reconstruction from limited leads using deep learning
- **ID / Year / Venue:** P072 / 2025 / Communications Medicine
- **Model & task:** GAN (Pulse2Pulse/pix2pix-inspired U-Net generator, WGAN-GP) and U-Net (MSE) baseline; lead-reconstruction (lead I or I+II -> 12-lead)
- **Losses:** GAN: WGAN-GP adversarial (with gradient clipping) + L1 reconstruction; U-Net: MSE
- **Evaluation:** Per-lead RMSE; GE MUSE 12SL measurements (RR, QT, PR, QRS duration, R/S/T peak, ST amplitudes); Student t-test (means); F-test (variances); Bland-Altman plots; R2/Pearson between error and true amplitude (regression-to-mean); inter-lead marker correlations real vs reconstructed
- **Data:** PTB-XL v1.0.3 (9514 individuals; test 952 normal ECGs); leads: 1 or 2 input -> 8 independent leads (12-lead derived); fs: 500; length: 10
- **Takeaway for ECGEN-Eval:** Add variance-ratio (F-test), error-vs-amplitude correlation and inter-lead correlation preservation checks to detect regression-to-mean.
- *Extraction source: full-text*
