# Lightweight Multi-task CNN for ECG Diagnosis with GRU-Diffusion
- **ID / Year / Venue:** P100 / 2025 / arXiv
- **Model & task:** Diffusion (DDPM U-Net with embedded 16-layer GRU, 'GRU-Diffusion') + lightweight multi-task CNN classifier (DFNet); augmentation (minority-class beats for classification)
- **Losses:** Generator: standard DDPM objective (not explicitly stated); classifier: cross-entropy for two tasks + L2 regularization
- **Evaluation:** FID (Fréchet distance on PCA-reduced signals); mean and std of DTW on randomly paired real/generated signals; KL divergence between Welch PSDs; downstream Accuracy, Precision, Recall, F1; params/FLOPs
- **Data:** MIT-BIH Arrhythmia (12 classes); PTB Diagnostic ECG Database (9 classes, 12 standard leads); leads: 1 (all data split into single-lead signals); fs: 250 (resampled); length: ~2.05 (512 samples)
- **Takeaway for ECGEN-Eval:** PSD-KL via Welch and DTW std (as spread indicator) are cheap complements; label PCA-based FD clearly as such.
- *Extraction source: full-text*
