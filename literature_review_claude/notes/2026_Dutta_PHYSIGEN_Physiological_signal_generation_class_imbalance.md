# PHYSIGEN: Physiological signal generation for class imbalance mitigation based on generative AI and machine learning
- **ID / Year / Venue:** P115 / 2026 / Innovation and Emerging Technologies
- **Model & task:** GAN (class-conditional CTGAN, tabular) vs SMOTE; task: augmentation
- **Losses:** CTGAN adversarial loss (details unknown)
- **Evaluation:** downstream emotion-classification accuracy (DTree, SVM, LR, LDA, kNN); minority-class recognition rate (tags: utility-TSTR)
- **Data:** ASCERTAIN (ECG, EEG, GSR features); leads: unknown (abstract only); fs: unknown (abstract only) Hz; length: unknown (abstract only) s
- **Notes:** Tabular feature synthesis, not ECG waveforms. SVM accuracy 46.8% -> 71.74% with CTGAN; HAHV minority recall 3.8% -> 47.2%.
- **Takeaway for ECGEN-Eval:** Marginal relevance: tabular-feature GAN, utility-only.
- *Extraction source: abstract-only*
