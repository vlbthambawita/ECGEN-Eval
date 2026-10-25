# ABC-GAN: An Attention-Based Conditional GAN with DTW Loss for ECG Signal Generation to Address Class Imbalance
- **ID / Year / Venue:** P010 / 2026 / Journal of Information Systems and Telecommunication (JIST)
- **Model & task:** Attention conditional WGAN-GP for class-specific heartbeats
- **Losses:** WGAN-GP + lambda*DTW loss (compared with MSE and KL alternatives)
- **Evaluation:** DTW, MSE, KL histogram divergence; ResNet34 precision/recall/F1/accuracy after augmentation
- **Data:** MIT-BIH, 7 classes, 256 Hz beats
- **Takeaway for ECGEN-Eval:** Per-class DTW-to-nearest-real outlier rate is a useful plausibility/rejection metric; report per-class.
- *Extraction source: full-text*
