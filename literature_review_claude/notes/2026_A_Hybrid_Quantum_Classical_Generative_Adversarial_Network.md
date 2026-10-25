# Hybrid Quantum-Classical Generative Adversarial Network for Synthetic 12-Lead Electrocardiogram Signal Generation
- **ID / Year / Venue:** P090 / 2026 / n/a
- **Model & task:** GAN (hybrid quantum-classical: PennyLane parameterised quantum circuit generator + 1-D CNN discriminator); task: unconditional
- **Losses:** adversarial GAN loss (parameter-shift rule gradients); details unknown
- **Evaluation:** Fréchet Distance (FD); visual check of P/QRS/T and inter-lead relationships (tags: distribution)
- **Data:** MIT-BIH Arrhythmia; leads: 12 (claimed); fs: unknown (abstract only) Hz; length: unknown (abstract only) s
- **Notes:** QGAN FD 12.3±2.1 vs classical CNN 15.8±3.2 and LSTM 18.4±4.1. Note: claims 12-lead generation from MIT-BIH, which has only 2 leads — internally questionable.
- **Takeaway for ECGEN-Eval:** Shows FD alone used for claims; sanity-check dataset/lead consistency.
- *Extraction source: abstract-only*
