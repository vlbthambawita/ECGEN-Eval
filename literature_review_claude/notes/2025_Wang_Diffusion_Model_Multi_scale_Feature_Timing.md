# Diffusion Model-Based Multi-scale Feature and Timing Consistency Enhancement for ECG Signal Generation
- **ID / Year / Venue:** P050 / 2025 / Lecture Notes in Computer Science (KSEM 2025, LNAI 15919)
- **Model & task:** DDPM with dilated-conv UNet fed by db4 wavelet sub-bands plus a lightweight 4-head Transformer bottleneck; unconditional single-lead ECG generation for augmentation
- **Losses:** DDPM noise MSE + 0.5 DTW alignment loss to real signals + 0.3 wavelet-domain matching loss
- **Evaluation:** MSE, FD (unspecified features), variance, cardiologist score, QRS duration error, P/QRS/T timing deviations, RR-interval SD, DTW, augmentation accuracy/F1, compute cost, t-tests [fidelity, distribution, diversity, clinical, expert, utility-TSTR, efficiency]
- **Data:** MIT-BIH Arrhythmia, PTB Diagnostic; leads: single-channel (MLII/V1, II); fs: 360 Hz; length: 5 s clips
- **Notes:** vs single-scale DDPM: MSE 0.032 vs 0.041, FD 24.6 vs 28.3, expert 4.2 vs 3.5, RR SD 13.3 ms (real 12.5); ACC 92.3→95.6%. Pairing for MSE/DTW in an unconditional setting is not defined, the FD embedding is unstated, and the reference list has obvious errors, so numbers are weakly reproducible.
- **Takeaway for ECGEN-Eval:** The RR-interval-variability and fiducial-timing comparisons are what ECGEN-Eval's hrv metric and feature extractor already provide; ECGEN-Eval should require that any FD report names its feature space (fd handcrafted vs fed backbone) and that paired metrics state the pairing rule.
- *Extraction source: full-text*
