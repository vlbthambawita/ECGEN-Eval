# Improving Diagnostic Performance through Synthetic Beat Generation: A Hybrid Framework Combining Undersampling and Generative Oversampling for Balanced ECG Learning
- **ID / Year / Venue:** P092 / 2025 / IEEE Global Conference for Advancement in Technology (GCAT)
- **Model & task:** GAN (WGAN-GP, Conv1DTranspose generator + 1D-CNN critic) + NearMiss undersampling; class-balanced beat augmentation (5 classes)
- **Losses:** WGAN-GP (Wasserstein + gradient penalty)
- **Evaluation:** RBF-SVM accuracy, precision, recall, F1, confusion matrix only [utility-TSTR]
- **Data:** MIT-BIH Arrhythmia (Kaggle 187-sample beat version, 87,553 beats); leads: 1; fs: not reported (likely 125) Hz; length: not reported (187 samples) s
- **Notes:** Macro F1 0.89 on imbalanced data vs perfect 1.00 on every metric after balancing - almost certainly because synthetic beats are in the test split. No waveform, distributional or clinical evaluation of the generated beats.
- **Takeaway for ECGEN-Eval:** Cite as a cautionary example: augmentation results must be computed on a real-only, patient-disjoint test set, and ECGEN-Eval reports should pair any utility claim with direct fidelity/diversity metrics on the synthetic beats.
- *Extraction source: full-text*
