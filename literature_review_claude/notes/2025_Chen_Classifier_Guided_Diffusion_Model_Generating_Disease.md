# Classifier-Guided Diffusion Model for Generating Disease-Specific ECG Data: A Case Pilot Study on Inferior Myocardial Infarction
- **ID / Year / Venue:** P033 / 2025 / IEEE EMBC 2025
- **Model & task:** DDPM with 1D U-Net trained only on normal lead II ECGs, steered to inferior MI by classifier guidance (CNN normal-vs-IMI, w 30); class-conditional synthesis for augmentation/substitution
- **Losses:** DDPM noise-prediction MSE (1000 steps); cross-entropy for guidance classifier
- **Evaluation:** Normal-vs-IMI classifier precision/F1 with 0-100% synthetic IMI substitution; Q/R-ratio (Q-wave depth) distribution of real vs generated IMI; manual screening; annotated examples [utility-TSTR, clinical, conditional]
- **Data:** PTB-XL (9514 normal, 3271 IMI); leads: 1 (II); fs: 100 Hz; length: 10 s
- **Notes:** F1 0.761 (real) vs 0.792 (1000 synthetic) vs 0.744 (all synthetic IMI). Generated Q/R peak ~0.35 vs real ~0.25. Synthetic samples were hand-picked (1000 of 30000) and the merged datasets were split 7:2:1, so test sets include synthetic data; the utility result is not a clean TSTR.
- **Takeaway for ECGEN-Eval:** ECGEN-Eval's feature extractor could add pathology-targeted features (Q/R ratio, Q-wave duration) compared as real-vs-synthetic distributions per class, and reports should state any post-hoc sample filtering and its acceptance rate.
- *Extraction source: full-text*
