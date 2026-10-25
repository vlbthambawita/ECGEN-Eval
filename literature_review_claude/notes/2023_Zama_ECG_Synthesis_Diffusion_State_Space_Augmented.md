# ECG Synthesis via Diffusion-Based State Space Augmented Transformer
- **ID / Year / Venue:** P062 / 2023 / Sensors
- **Model & task:** Diffusion (DDPM with State Space Augmented Transformer denoiser, DSAT-ECG; SSSD-ECG-like); class-cond (12 multilabel rhythm classes)
- **Losses:** DDPM simplified noise-prediction MSE
- **Evaluation:** average DTW; average MMD (Gaussian kernel); 'authenticity': multilabel accuracy and macro AUROC of a ResNet-1D classifier trained on real data evaluated on synthetic vs real test sets (TRTS) (tags: fidelity;distribution;utility-TSTR)
- **Data:** PTB-XL (patient-wise split 17,441/2,193/2,203); leads: 12 (8 generated: I, aVF, V1-V6; remaining 4 derived via Einthoven/Goldberger); fs: 100; length: 10
- **Notes:** DTW 7.174, MMD 4.603e-3 vs SSSD-ECG 7.481/4.784e-3; TRTS acc 95.84/AUROC 94.56 vs real 96.38/94.67. Pitfall: metrics computed in batches of 16 samples — tiny-sample MMD/DTW are noisy. Admits synthetic data cannot fully replace real for training.
- **Takeaway for ECGEN-Eval:** TRTS (real-trained classifier scored on synthetic vs real) is a cheap class-conditional check; warn about small-batch MMD estimates.
- *Extraction source: full-text*
