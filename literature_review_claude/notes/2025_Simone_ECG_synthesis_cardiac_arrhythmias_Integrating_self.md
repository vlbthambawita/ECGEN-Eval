# ECG synthesis for cardiac arrhythmias: Integrating self-supervised learning and generative adversarial networks
- **ID / Year / Venue:** P061 / 2025 / Artificial Intelligence in Medicine
- **Model & task:** GAN (conditional, with self-supervised learning; ECGAN); class-cond
- **Losses:** adversarial + self-supervised objective (details unknown)
- **Evaluation:** morphological plausibility; arrhythmia classification accuracy (augmentation, +2.4%); training stability (tags: fidelity;utility-TSTR)
- **Data:** MIT-BIH; BIDMC (CHF); PTB; leads: unknown (abstract only); fs: unknown (abstract only); length: unknown (abstract only)
- **Notes:** Proposes a 'workflow for synthetic time series assessment'; classes: CHF, MI, sinus rhythm, PVC.
- **Takeaway for ECGEN-Eval:** Combine morphological plausibility checks with augmentation gain per class.
- *Extraction source: abstract-only*
