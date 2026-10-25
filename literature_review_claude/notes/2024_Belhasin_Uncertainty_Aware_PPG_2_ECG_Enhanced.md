# Uncertainty-Aware PPG-2-ECG for Enhanced Cardiovascular Diagnosis using Diffusion Models
- **ID / Year / Venue:** P148 / 2024 / arXiv
- **Model & task:** Diffusion (conditional DDPM-style denoiser for PPG->ECG; reverse ECG->PPG model for data completion); UA-P2E uncertainty-aware classification; PPG2ECG
- **Losses:** diffusion noise-prediction (denoiser epsilon(X_t,Y,t)); classifier cross-entropy
- **Evaluation:** RMSE (single sample and MMSE/mean of K=100 samples); Frechet Distance (1-FD single sample, 100-FD multi-sample); ROC/AUROC of classification strategies; risk-coverage curves for selective classification; conformal calibration guarantees; MSE and PSNR training curves; pairwise synthetic ECG distances
- **Data:** MIMIC-III matched waveform (PPG-ECG pairs); PhysioNet/CinC 2021 (11 lead-II-detectable conditions, with synthesized PPG); leads: 1 (lead II); fs: 125; length: ~8 (1024 samples)
- **Takeaway for ECGEN-Eval:** For stochastic generators, report both per-sample and mean-of-samples distortion plus distributional metrics (perception-distortion trade-off).
- *Extraction source: full-text*
