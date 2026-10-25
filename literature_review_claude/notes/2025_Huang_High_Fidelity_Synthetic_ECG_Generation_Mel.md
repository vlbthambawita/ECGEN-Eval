# High-Fidelity Synthetic ECG Generation via Mel-Spectrogram Informed Diffusion Training
- **ID / Year / Venue:** P089 / 2025 / arXiv
- **Model & task:** MIDT-ECG: SSSD-ECG diffusion with Mel-spectrogram loss and disentangled demographic conditioning
- **Losses:** MSE denoising + beta * multi-resolution Mel-spectrogram L1
- **Evaluation:** RMSE/MSE/SNR, Fourier and Hausdorff distance, SSIM, MIR, NNAA, inter-lead correlation error, label faithfulness, AUROC substitution/augmentation
- **Data:** PTB-XL, 12-lead, 100 Hz, 10 s
- **Takeaway for ECGEN-Eval:** Adopt inter-lead correlation-matrix error, NNAA/MIR privacy metrics, and classifier-based label faithfulness.
- *Extraction source: full-text*
