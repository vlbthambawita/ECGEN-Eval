# Principal component conditional generative adversarial networks for imbalanced ECG classification enhancement
- **ID / Year / Venue:** P119 / 2025 / PLoS ONE
- **Model & task:** GAN (PCA-based conditional GAN with Transformer encoder-decoder, 'PCA-CGAN'); class-cond / augmentation (imbalanced arrhythmia, generates PCA components)
- **Losses:** WGAN-GP (λ=10) + L1/L2; encoder-decoder PCA reconstruction MSE
- **Evaluation:** NPRD, NRMSE, NMAE (amplitude-range-normalized PRD/RMSE/MAE); leave-one-out and 5-fold CV; Wasserstein distance; Jensen-Shannon divergence; 2-sample KS test p-value; principal component retention rate; frequency-domain correlation coefficient; morphological similarity; downstream ResNet/other Precision, Recall, F1
- **Data:** MIT-BIH Arrhythmia (43 patients); leads: 1 (implied; not explicitly stated); fs: 360; length: not reported (beat-level)
- **Takeaway for ECGEN-Eval:** Adopt range-normalized NRMSE/NPRD/NMAE and consider QRS-weighted errors to counter dilution by isoelectric segments.
- *Extraction source: full-text*
