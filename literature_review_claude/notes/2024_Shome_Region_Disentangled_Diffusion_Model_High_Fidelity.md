# Region-Disentangled Diffusion Model for High-Fidelity PPG-to-ECG Translation
- **ID / Year / Venue:** P126 / 2024 / Proceedings of the AAAI Conference on Artificial Intelligence
- **Model & task:** Diffusion (RDDM: region-disentangled DDPM with ROI (QRS)-guided forward process, two denoisers); PPG2ECG
- **Losses:** lambda1*||mu*eps - eps_theta(x_t^m,c,t)||^2 (ROI/QRS noise) + lambda2*||x_t^m - rho_phi(x_t,c,t)||^2 (non-ROI denoising)
- **Evaluation:** RMSE; Fréchet Distance (FD, following CardioGAN); CardioBench: HR estimation MAE (bpm, Hamilton detector), AFib detection F1/accuracy, stress and affect classification F1/accuracy, diabetes detection, SBP/DBP estimation MAE (train on real, test on generated) [fidelity; clinical; utility-TSTR; efficiency]
- **Data:** WESAD; DALIA; CAPNO; BIDMC; MIMIC-AFib (training); CardioBench: WESAD, DALIA, MIMIC-AFib, PPG-BP, Cuffless-BP; leads: 1 (Lead II); fs: 128 (resampled) Hz; length: 4 (training windows) s
- **Notes:** Introduces CardioBench: train-on-real/test-on-generated downstream benchmark with real-test performance as upper bound. Only 10 sampling steps. Subject-independent evaluation.
- **Takeaway for ECGEN-Eval:** TRTS downstream benchmark with real-data upper bound and HR-MAE are useful; clarify FD (curve) vs FID-style naming.
- *Extraction source: full-text*
