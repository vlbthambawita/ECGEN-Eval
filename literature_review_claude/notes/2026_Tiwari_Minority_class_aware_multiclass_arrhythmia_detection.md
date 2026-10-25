# Minority class-aware multiclass arrhythmia detection using conditional GAN augmentation
- **ID / Year / Venue:** P103 / 2026 / Scientific reports
- **Model & task:** cWGAN-GP (with auxiliary classifier) augmenting minority MIT-BIH beats + multi-stream classifier
- **Losses:** WGAN-GP + auxiliary classification loss
- **Evaluation:** DTW, SSIM; macro/per-class F1, AUC, 5-fold CV; edge inference cost
- **Data:** MIT-BIH, AAMI 5 classes, 360 Hz single beats
- **Takeaway for ECGEN-Eval:** Utility via per-class minority F1 gains is the main signal; fidelity metrics are thin - typical of augmentation papers.
- *Extraction source: full-text*
