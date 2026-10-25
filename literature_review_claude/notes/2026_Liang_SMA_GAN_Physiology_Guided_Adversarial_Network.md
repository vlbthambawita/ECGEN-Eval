# SMA-GAN: A Physiology-Guided Adversarial Network with Attention and Spectral Constraints for Imbalanced ECG Synthesis
- **ID / Year / Venue:** P132 / 2026 / IEEE International Conference on Acoustics Speech and Signal Processing
- **Model & task:** GAN (SMA-GAN: Physiology-Guided Modulation Attention on QRS + spectral constraint); augmentation (minority-class heartbeat synthesis)
- **Losses:** adversarial loss + Spectral Consistency Constraint (frequency-domain regularization)
- **Evaluation:** multiple generation-quality metrics (unspecified in abstract); classifier F1-score (esp. fusion beats)
- **Data:** MIT-BIH Arrhythmia; leads: unknown (abstract only); fs: unknown (abstract only); length: heartbeat segments
- **Takeaway for ECGEN-Eval:** Spectral consistency as a loss mirrors PSD-based evaluation; avoid using the same spectral term as both loss and sole metric.
- *Extraction source: abstract-only*
