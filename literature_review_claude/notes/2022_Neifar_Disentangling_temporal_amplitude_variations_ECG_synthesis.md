# Disentangling temporal and amplitude variations in ECG synthesis using anchored GANs
- **ID / Year / Venue:** P176 / 2022 / ACM/SIGAPP Symposium on Applied Computing (SAC)
- **Model & task:** GAN (anchored, prior-knowledge morphological patterns; temporal/amplitude disentanglement); unconditional / class-cond (beats) + augmentation
- **Losses:** adversarial + anchor/prior morphology (details unknown, abstract only)
- **Evaluation:** unknown (abstract only); ECG classification improvement [utility-TSTR]
- **Data:** MIT-BIH Arrhythmia; leads: unknown (abstract only); fs: unknown (abstract only) Hz; length: unknown (abstract only; beat-level) s
- **Notes:** Separates temporal (time-warping) and amplitude variation; evaluation details not in abstract.
- **Takeaway for ECGEN-Eval:** Separate timing (DTW warp) and amplitude error components when reporting distances.
- *Extraction source: abstract-only*
