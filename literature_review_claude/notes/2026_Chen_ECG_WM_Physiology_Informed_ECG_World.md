# ECG-WM: A Physiology-Informed ECG World Model for Clinical Intervention Simulation
- **ID / Year / Venue:** P065 / 2026 / arXiv
- **Model & task:** ECG-WM: physiology-regularized latent diffusion world model simulating drug effects on 12-lead ECG
- **Losses:** DDPM epsilon loss + latent ODE-energy regularizer (lambda=0.1); frozen VAE (recon + KL)
- **Evaluation:** MSE/MAE/RMSE; QTc/PR/Tpeak-Tend normal-range classification agreement; foundation-model diagnostic-score change correlation
- **Data:** MIMIC-IV-ECG + clinical, FDA drug-response ECG sets, in-house OOD
- **Takeaway for ECGEN-Eval:** Clinical interval normal-range agreement and foundation-model label-probability agreement are strong conditional-fidelity metrics.
- *Extraction source: full-text*
