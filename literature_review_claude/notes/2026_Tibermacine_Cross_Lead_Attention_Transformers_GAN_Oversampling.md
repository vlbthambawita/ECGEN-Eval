# Cross-Lead Attention Transformers with GAN Oversampling for Robust ECG Arrhythmia Detection
- **ID / Year / Venue:** P040 / 2026 / Electronics
- **Model & task:** GAN (beat-level oversampling) + cross-lead Transformer classifier; augmentation (class-imbalanced arrhythmia beats)
- **Losses:** unknown (abstract only)
- **Evaluation:** accuracy; F1-score; AUC (downstream classification, 10 runs); attention visualizations
- **Data:** MIT-BIH Arrhythmia (16 beat classes, 2 leads); external: ECG5000, St Petersburg INCART (12-lead); leads: 2 (MIT-BIH); 1 (ECG5000); 12 (INCART); fs: unknown (abstract only); length: beat segments (abstract only)
- **Takeaway for ECGEN-Eval:** Example of utility-only evaluation of GAN augmentation; ECGEN-Eval should pair TRTS/TSTR utility with direct fidelity metrics.
- *Extraction source: abstract-only*
