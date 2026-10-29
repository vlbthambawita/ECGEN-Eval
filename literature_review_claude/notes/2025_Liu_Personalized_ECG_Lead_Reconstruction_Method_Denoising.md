# A Personalized ECG Lead Reconstruction Method Based on Denoising Diffusion Model
- **ID / Year / Venue:** P006 / 2025 / AICI 2025 (ACM)
- **Model & task:** Conditional diffusion (DDPM with DDIM-style 'directional' non-Markovian noising, DiffWave-like dilated residual blocks) conditioned on lead II; pretrained on PTB then fine-tuned on a few records of the target patient; personalised II→12 lead reconstruction
- **Losses:** MSE noise-prediction loss (200 steps, beta 1e-4 to 0.02)
- **Evaluation:** Per-lead Pearson CC by diagnostic class; ResNet18 12-class MI localisation (ACC, macro P/R/F1, confusion matrix) on real vs reconstructed; comparison with re-implemented LSTM, GAN, U-Net, shifted-diffusion baselines [fidelity, utility-TSTR, clinical]
- **Data:** PTB Diagnostic ECG Database (patient-specific split); leads: 1 in -> 12 out; fs: 360 Hz; length: 5 s
- **Notes:** Mean CC 0.864 across classes (MI 0.814, BBB 0.770); 0.826 vs 0.834 for shifted-diffusion baseline in head-to-head table despite SOTA claim. MI localisation ACC 0.97 / F1 0.96 on reconstructed, within 2.2% of real. Only correlation reported; per-signal min-max normalisation removes amplitude information.
- **Takeaway for ECGEN-Eval:** For paired lead-reconstruction tasks, ECGEN-Eval should report per-lead Pearson CC alongside amplitude-sensitive errors (mae/RMSE, prd) on un-normalised signals, since correlation alone hides amplitude errors.
- *Extraction source: full-text*
