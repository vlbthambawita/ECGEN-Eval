# Progressive Two-Stage ECG Signal Generation: From Structural Skeletons to High-Fidelity Detail Refinement
- **ID / Year / Venue:** P164 / 2025 / IEEE International Conference on Bioinformatics and Biomedicine (BIBM)
- **Model & task:** Other (two-stage generator: square-wave structural skeleton generator + attention-based refinement module); class-cond / augmentation (AFIB, AT, AF)
- **Losses:** unknown (abstract only)
- **Evaluation:** Euclidean distance (ED) in feature space (12.815); KL divergence (KLD) in feature space (0.325); downstream classification F1 (0.672 vs 0.632 best baseline)
- **Data:** Resting ECG Segmentation Dataset; leads: unknown (abstract only); fs: unknown (abstract only); length: unknown (abstract only)
- **Takeaway for ECGEN-Eval:** Segmentation-derived skeletons suggest evaluating wave-boundary/segment-duration agreement.
- *Extraction source: abstract-only*
