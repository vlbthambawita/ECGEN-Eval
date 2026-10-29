# Exploring latent diffusion models for ECG generation on the minute scale
- **ID / Year / Venue:** P074 / 2025 / Computer Methods and Programs in Biomedicine
- **Model & task:** Diffusion (latent: VQ-VAE, 1024-token codebook + 1D U-Net DDIM; ECGEN); conditional sinus/AFib 30 s generation, 90 s inpainting, unconditional 320 s generation
- **Losses:** VQ-VAE MSE reconstruction + DDIM noise-prediction L2
- **Evaluation:** AFib-detector conditioning AUC; HR/SDNN distributions vs training set (KS, permutation tests); inpainting HR consistency; averaged-beat RMSE/MAE/DTW/FD and PR/QRS/QT/ST/Tpeak-Tend intervals; gap-inpainting error vs interpolation; expert implausibility rate [clinical, distribution, conditional, fidelity, expert]
- **Data:** Private Charité stroke-unit single-lead ECGs; leads: 1; fs: 512 Hz; length: 30 / 90 / 320 s
- **Notes:** AUC 0.98 (but ~12% sinus prompts read as AFib). Large model: HR SD collapses (12.22 → 3.40) while SDNN inflates (89 → 398), with ~1.5% implausible beats (double R peaks). Inpainting halves error vs interpolation. Morphology metrics on grand-average beats only.
- **Takeaway for ECGEN-Eval:** Strong case for distribution-level HR/HRV tests (KS + spread ratio, not just mean differences) on long recordings and a beat-validity/implausible-morphology rate; caveat that average-beat similarity metrics can look good while HRV distributions are badly off.
- *Extraction source: full-text*
