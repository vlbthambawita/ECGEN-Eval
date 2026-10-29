# Physiologically Validated Synthetic ECG Generation via LLM-Guided Constraint Enforcement
- **ID / Year / Venue:** P159 / 2026 / Lecture notes in computer science (ICPR 2026 Workshops)
- **Model & task:** Hybrid (LLM-produced JSON physiological envelopes + rejection sampling over interpolation, MLP WGAN-GP and 1D-CNN WGAN-GP); per-class AAMI beat augmentation
- **Losses:** WGAN-GP; constraints enforced post hoc, not in the loss
- **Evaluation:** rejection rate; TRTS/TSTR; per-class MMD; DTW ratio; TOST equivalence on 8 morphological features; pairwise cosine diversity; local-morphology audit; membership inference; CNN-BiLSTM macro/per-class F1 over 10 seeds [fidelity, distribution, clinical, diversity, utility-TSTR, privacy, efficiency, conditional]
- **Data:** MIT-BIH Arrhythmia (DS1/DS2 inter-patient); leads: 1; fs: 360 Hz; length: ~0.69 s (250-sample beat)
- **Notes:** Even the 1D-CNN-GAN yields 96.3% physiologically invalid N beats (S/V/F 15.8/19.1/36.1%); TRTS 95.7%, TSTR 82.1%; TOST equivalence 6/8 (S), 5/8 (V), 1/8 (N); no significant macro-F1 gain inter-patient; only 13% of envelope-passing beats pass a local smoothness audit. LLM envelopes are statistically equivalent to hand-written rules (p=0.35).
- **Takeaway for ECGEN-Eval:** Add a per-beat physiological validity rate (guideline envelopes on QRS width, amplitude, RR from the feature extractor) plus TOST equivalence testing on clinical features and a local-smoothness check, reporting the fraction of samples passing rather than only distribution-level distances.
- *Extraction source: full-text*
