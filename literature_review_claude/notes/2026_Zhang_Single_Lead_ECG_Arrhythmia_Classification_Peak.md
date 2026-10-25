# Single-Lead ECG Arrhythmia Classification Based on Peak-Enhanced Attention Network and Quality-Aware GAN Data Augmentation Framework
- **ID / Year / Venue:** P131 / 2026 / Sensors (Basel, Switzerland)
- **Model & task:** GAN (Quality-Aware GAN, QA-GAN: CNN + BiLSTM, kurtosis-based dynamic soft-label discriminator); augmentation (class-cond AF minority class)
- **Losses:** Generator: standard adversarial loss; Discriminator: dynamic soft-label BCE with real-sample target y = α + (1−α)·tanh(log(K(x)+1)/5) from signal kurtosis K (α=0.7 best)
- **Evaluation:** visual comparison; t-SNE overlap of real vs synthetic AF features; downstream classifier precision, sensitivity, specificity, accuracy, F1, macro-F1, AUC/ROC, PR curves; comparison vs SMOTE, random oversampling, class-weighted loss; noise robustness (tags: utility-TSTR)
- **Data:** PhysioNet/CinC Challenge 2017 (AliveCor, 8,528 recordings); MIT-BIH Arrhythmia (classifier adaptability); leads: 1; fs: 300; length: 10 (segments)
- **Notes:** Generator quality evaluated only visually and via downstream augmentation (F1 0.793 baseline → 0.816 with QA-GAN vs 0.809 class-weighted loss). Kurtosis used as a signal-quality index during training — could also serve as an SQI metric for synthetic ECGs.
- **Takeaway for ECGEN-Eval:** Kurtosis-based SQI is a cheap reference-free quality metric; also shows need to compare augmentation against SMOTE/class-weighting baselines.
- *Extraction source: full-text*
