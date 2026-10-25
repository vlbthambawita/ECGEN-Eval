# Data imbalance in cardiac health diagnostics using CECG-GAN
- **ID / Year / Venue:** P041 / 2024 / Scientific reports
- **Model & task:** GAN (conditional, TimeGAN-style with Transformer encoder/decoder/generator/discriminator; 'CECG-GAN'); class-cond / augmentation (imbalanced arrhythmia)
- **Losses:** Adversarial (conditional GAN) loss + TimeGAN-style embedding/recovery reconstruction and supervised latent-matching loss (details not formally given)
- **Evaluation:** PRD; Fréchet Distance (discrete, per-pair); RMSE; MAE; downstream classifier Precision, Recall, F1, Accuracy; per-patient evaluation; comparison to BiLSTM-CNN GAN, LSTM-AE GAN, LSTM-VAE GAN, SimGAN
- **Data:** MIT-BIH Arrhythmia; CPSC2020; leads: 1 (implied single-lead beats; not explicitly stated); fs: 360 (MIT-BIH); length: windows of 200-400 samples (~0.55-1.1 s beats)
- **Takeaway for ECGEN-Eval:** Clarify FD naming (discrete Fréchet vs Fréchet-Gaussian) and warn against classifier-guided sample selection in utility evaluation.
- *Extraction source: full-text*
