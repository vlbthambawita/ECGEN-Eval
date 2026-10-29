# Transformer-Based Generative Adversarial Network With Multi-Scale Temporal Attention for ECG Synthesis and PQRST Feature Preservation
- **ID / Year / Venue:** P147 / 2026 / IEEE Access
- **Model & task:** TransGAN: Transformer generator with temporal self-attention, hierarchical multi-scale (beat/rhythm/sequence) transformer patch discriminator, PQRST-constrained loss; unconditional 10 s ECG synthesis for augmentation with class-weighted BCE
- **Losses:** Adversarial BCE + weighted BCE + PQRST feature-consistency loss + temporal coherence term
- **Evaluation:** MSE, DTW, Wasserstein distance, PQRST feature accuracy, SNR, sample entropy, RR/QRS CV with t-test, spectra, augmentation accuracy, unquantified medical review, delineator validation, ablations [fidelity, distribution, clinical, expert, utility-TSTR, diversity]
- **Data:** MIT-BIH Arrhythmia, PTB-XL, simulated ECG; leads: single-channel; fs: 250 Hz; length: 10 s
- **Notes:** MIT-BIH MSE 0.042 / DTW 2.29 / WD 0.120 / PQRST acc 94.1%; augmentation 82.5→90.5%. Unconditional samples compared point-wise to real with no pairing rule; real data denoised but synthetic not; abstract's '7.2%' gain disagrees with body.
- **Takeaway for ECGEN-Eval:** The PQRST-within-tolerance accuracy and RR/QRS coefficient-of-variation comparisons map directly onto ECGEN-Eval's feature extractor and could become a 'fiducial agreement' metric, while ECGEN-Eval should warn that applying different preprocessing to real and synthetic sets biases snr/psd-type comparisons.
- *Extraction source: full-text*
