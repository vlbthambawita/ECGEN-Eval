# Autoencoder-based Arrhythmia Detection using Synthetic ECG Generation Technique
- **ID / Year / Venue:** P021 / 2024 / Annual International Conference of the IEEE Engineering in Medicine and Biology Society (EMBC)
- **Model & task:** GAN (TabGAN tabular GAN treating each beat as a feature row) + dense autoencoder anomaly detector; unconditional (normal-beat synthesis for augmentation of AE anomaly detector)
- **Losses:** standard TabGAN adversarial loss; AE reconstruction loss
- **Evaluation:** AUC-ROC and AUC-PR of AE anomaly detector trained on real normal + 5x/10x synthetic normal beats; comparison with DAGMM, GMM, iForest, LOF [utility-TSTR]
- **Data:** MIT-BIH Arrhythmia (Kaggle-style preprocessed heartbeat set, 109,446 beats, 5 AAMI classes); leads: 1; fs: 125 (resampled from 360) Hz; length: not reported (fixed-length beat segments) s
- **Notes:** AUC-ROC 0.656 -> 0.677 (5x) -> 0.686 (10x), AUC-PR 0.826 -> 0.854 -> 0.867; still below DAGMM 0.762. No direct signal-fidelity, distribution or visual evaluation of the synthetic beats; despite the abstract, Algorithm 1 trains the AE on synthetic + real normal data (augmentation, not pure train-on-synthetic); a generic tabular GAN ignores temporal structure.
- **Takeaway for ECGEN-Eval:** An example of utility-only evaluation of a generic tabular GAN; ECGEN-Eval reports should always pair downstream gains with direct fidelity/diversity metrics (mmd, pr_dist, hrv, sqi) so beat realism is not inferred from a small anomaly-detection AUC change.
- *Extraction source: full-text*
