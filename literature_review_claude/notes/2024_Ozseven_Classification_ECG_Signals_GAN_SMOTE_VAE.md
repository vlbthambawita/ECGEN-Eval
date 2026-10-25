# Classification of ECG Signals Using GAN, SMOTE, and VAE Data Augmentation Methods: Synthetic vs. Real
- **ID / Year / Venue:** P031 / 2024 / Bitlis Eren Üniversitesi Fen Bilimleri Dergisi
- **Model & task:** GAN (vanilla GAN, 2D conv) and VAE (2-layer CNN encoder/decoder) compared with SMOTE; augmentation (class-imbalanced heartbeat classification)
- **Losses:** standard minimax GAN loss (Goodfellow); VAE (reparameterization; loss not explicitly stated)
- **Evaluation:** accuracy; specificity; recall; F1-score of a 2D-CNN classifier under real-only, synthetic-only, train-synthetic-test-real, and real+synthetic settings
- **Data:** MIT-BIH Arrhythmia (MLII lead, 4 AAMI classes F/N/S/V, 42 records); leads: 1 (MLII); fs: not reported (MIT-BIH native 360); length: single heartbeats rendered as images
- **Takeaway for ECGEN-Eval:** Shows why TSTR must be separated from train/test-on-synthetic; enforce patient-level splits in utility evaluation.
- *Extraction source: full-text*
