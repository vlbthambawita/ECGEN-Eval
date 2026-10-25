# Generation and Selection: A Self-Iterative Two-Stage Data Augmentation Method for Automated ECG Classification
- **ID / Year / Venue:** P082 / 2025 / IEEE Journal of Biomedical and Health Informatics
- **Model & task:** Diffusion (unconditional, Transformer-encoder guided) + pseudo-label selection (SiTs-ECG); augmentation (unconditional generation + pseudo-labelling)
- **Losses:** unknown (abstract only)
- **Evaluation:** Precision; Recall; F1; Accuracy (downstream classification, e.g., ECG-Transformer)
- **Data:** three real-world datasets incl. Apnea-ECG (others unknown (abstract only)); leads: unknown (abstract only); fs: unknown (abstract only); length: long-term ECG (abstract only)
- **Takeaway for ECGEN-Eval:** Classifier-confidence (pseudo-label) filtering could be an optional per-sample quality score; flag its selection bias.
- *Extraction source: abstract-only*
