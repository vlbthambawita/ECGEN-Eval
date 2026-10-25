# Improving Diagnostic Performance through Synthetic Beat Generation: A Hybrid Framework Combining Undersampling and Generative Oversampling for Balanced ECG Learning
- **ID / Year / Venue:** P092 / 2025 / IEEE Global Conference for Advancement in Technology (GCAT)
- **Model & task:** GAN (WGAN-GP) + NearMiss undersampling; augmentation (class-balanced beats, 5 AAMI classes)
- **Losses:** WGAN-GP adversarial (Wasserstein + gradient penalty)
- **Evaluation:** Downstream SVM accuracy, precision, recall, F1 (100% balanced vs ~89% F1 unbalanced)
- **Data:** MIT-BIH Arrhythmia; leads: unknown (abstract only); fs: unknown (abstract only); length: unknown (abstract only; beat-level)
- **Takeaway for ECGEN-Eval:** Cautionary example: utility-only evaluation with suspicious 100% scores; enforce real held-out test sets in TSTR.
- *Extraction source: abstract-only*
