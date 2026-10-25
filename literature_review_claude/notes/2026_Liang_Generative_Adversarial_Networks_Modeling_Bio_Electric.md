# Generative Adversarial Networks for Modeling Bio-Electric Fields in Medicine: A Review of EEG, ECG, EMG, and EOG Applications
- **ID / Year / Venue:** P085 / 2026 / Bioengineering
- **Model & task:** Survey (GANs for EEG/ECG/EMG/EOG); survey
- **Losses:** Catalogues GAN loss variants with formulas: WGAN (Wasserstein), WGAN-GP (gradient penalty), BGAN, EBGAN, LSGAN, conditional GAN/CWGAN; mentions physiological constraints in GAN losses and feature-loss functions for denoising
- **Evaluation:** Catalogued (synthesis): PRD; RMSE; FD; MAE; DTW; Fréchet/Euclidean distance; SSIM; FID; IS; sliced Wasserstein distance; MMD; Kappa; classification accuracy/F1/AUC; (denoising): SNR; RRMSE (time/frequency); CC; PSNR; MI; PRD
- **Data:** catalogued: MIT-BIH, PTB-XL and others across modalities; leads: various; fs: various; length: various
- **Takeaway for ECGEN-Eval:** Encode the subject-wise split warning and diagnostic-feature preservation (clinical features) alongside statistical similarity metrics.
- *Extraction source: full-text*
