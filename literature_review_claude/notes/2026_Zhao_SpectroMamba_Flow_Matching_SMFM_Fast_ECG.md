# SpectroMamba Flow Matching (SMFM): Fast ECG Generation via 2D Dual-Channel Spectrograms
- **ID / Year / Venue:** P162 / 2026 / IEEE International Conference on Acoustics Speech and Signal Processing
- **Model & task:** FlowMatching + SSM (bidirectional Mamba on 2-D real/imaginary spectrograms; weighted flow matching for class imbalance); task: class-cond / augmentation
- **Losses:** weighted flow-matching loss (class-imbalance weighting)
- **Evaluation:** DTW similarity; downstream classification F1-score (minority classes); inference steps/speed (tags: fidelity; utility-TSTR; efficiency)
- **Data:** MIT-BIH Arrhythmia; leads: unknown (abstract only); fs: unknown (abstract only) Hz; length: unknown (abstract only) s
- **Notes:** Targets 1000+ step diffusion inefficiency and 113:1 imbalance; DTW 0.176, F1 0.751.
- **Takeaway for ECGEN-Eval:** Report sampling cost (NFE/steps, time) alongside quality metrics.
- *Extraction source: abstract-only*
