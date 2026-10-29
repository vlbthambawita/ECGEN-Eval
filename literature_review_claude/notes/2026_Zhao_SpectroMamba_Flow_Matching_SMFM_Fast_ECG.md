# SpectroMamba Flow Matching (SMFM): Fast ECG Generation via 2D Dual-Channel Spectrograms
- **ID / Year / Venue:** P162 / 2026 / IEEE International Conference on Acoustics Speech and Signal Processing
- **Model & task:** FlowMatching + SSM (bidirectional Mamba on real/imaginary STFT spectrograms, 10-step DPM-Solver++, inverse STFT); class-conditional beat generation for augmentation
- **Losses:** inverse-frequency class-weighted flow-matching velocity MSE
- **Evaluation:** DTW; overall and per-class F1; TSTR and real+synthetic macro F1; inference time, memory, steps; ablations [fidelity, utility-TSTR, efficiency, conditional]
- **Data:** MIT-BIH Arrhythmia (78,798 187-sample beats, 5 classes); leads: 1; fs: not reported (likely 125) Hz; length: not reported (187 samples) s
- **Notes:** DTW 0.176, F1 0.751 vs DDPM-ECG 0.245/0.681; 0.28 s vs 28.4 s per batch; fusion F1 +71%; TSTR ~0.80 vs real ~0.92. DTW pairing and the classifier behind F1 are not described, and TSTR numbers are approximate; no distribution-level or clinical evaluation.
- **Takeaway for ECGEN-Eval:** Report cards should record DTW pairing mode (nearest-neighbour vs random pairs) and normalisation explicitly, and add sampling-time/steps as an efficiency field, since papers like this quote unreproducible DTW 'similarity' values.
- *Extraction source: full-text*
