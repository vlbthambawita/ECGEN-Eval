# Hybrid Quantum-Classical Generative Adversarial Network for Synthetic 12-Lead Electrocardiogram Signal Generation
- **ID / Year / Venue:** P090 / 2026 / International Conference on Recent Advancement in Electrical, Computer and Communication Technologies (IECCT)
- **Model & task:** GAN (4-qubit 4-layer PennyLane PQC generator + 1D-CNN discriminator, simulated); unconditional '12-lead' generation
- **Losses:** standard non-saturating GAN BCE losses
- **Evaluation:** Fréchet distance (unspecified features); SNR; loss-curve stability; qualitative morphology/inter-lead checks; latent traversal; SVM PVC F1 with augmentation [fidelity, distribution, diversity, utility-TSTR]
- **Data:** MIT-BIH Arrhythmia; leads: 12 (derived from 2 channels); fs: 360 Hz; length: 0.69 s (250 samples)
- **Notes:** FD 12.3±2.1 vs CNN 15.8 and LSTM 18.4; SNR 28.6 dB; +4.2% PVC F1. Methodologically weak: 12-lead signals cannot be reconstructed from MIT-BIH's two channels, FD features and SNR reference are undefined, clinical similarity claims lack numbers, and references look partly incorrect.
- **Takeaway for ECGEN-Eval:** Report cards should state the FD/FED feature space and reject SNR on unpaired samples; an inter-lead consistency check (Einthoven/Goldberger) would expose 'derived' 12-lead outputs whose precordial leads are not physically recoverable.
- *Extraction source: full-text*
