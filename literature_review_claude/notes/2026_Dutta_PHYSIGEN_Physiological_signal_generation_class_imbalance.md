# PHYSIGEN: Physiological signal generation for class imbalance mitigation based on generative AI and machine learning
- **ID / Year / Venue:** P115 / 2026 / Innovation and Emerging Technologies
- **Model & task:** GAN (per-class tabular CTGAN) vs SMOTE; augmentation of ECG/EEG/GSR feature vectors for 4-quadrant emotion recognition
- **Losses:** CTGAN adversarial loss
- **Evaluation:** accuracy and per-class recognition for DTree, SVM, LR, LDA, kNN; confusion matrices [utility-TSTR]
- **Data:** ASCERTAIN (ECG, EEG, GSR features); leads: not applicable; fs: not applicable Hz; length: not applicable s
- **Notes:** SVM accuracy 46.8% -> 71.74% (CTGAN) vs 51.2% (SMOTE); HAHV recall 3.8% -> 47.2%. Not ECG waveform generation; augmented data appears to be split 70:30 so synthetic samples likely leak into test; no direct quality check of synthetic features.
- **Takeaway for ECGEN-Eval:** Out of scope for waveform metrics; at most a cautionary example that augmentation gains must be measured on a real-only held-out test set.
- *Extraction source: full-text*
