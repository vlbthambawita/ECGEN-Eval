# Bayesian ECG reconstruction using denoising diffusion generative models
- **ID / Year / Venue:** P023 / 2023 / arXiv
- **Model & task:** Diffusion (conditional DDGM/DDPM, EDM-like U-Net; 'ECGDiff') used as Bayesian prior via MCGdiff SMC posterior sampling; class-cond (healthy beat conditioned on age, sex, RR); imputation (missing-lead reconstruction); denoising; anomaly detection
- **Losses:** DDPM denoising objective (equivalent to KL between inference and backward processes); no adversarial loss
- **Evaluation:** Earth Mover's Distance (EMD, L2 transport cost on ECG concatenated with age/sex/RR) generated vs test/train; out-of-distribution uncertainty via random-network-distillation-style ResNet pairs (B=10); rescaled Mahalanobis distance of posterior; R² score for missing-lead reconstruction vs Dower matrix; R² for QT-vs-RR vs Bazett/Fridericia/Framingham; ROC for MI detection (tags: distribution;fidelity;clinical)
- **Data:** PhysioNet/CinC Challenge 2021 (43,101 records; 28,167 patients normal beats, 468 MI patients); leads: 9 (aVL, aVR, aVF, V1-V6); fs: 250; length: 0.704 (single beat, R-192 ms to R+512 ms; 176 samples)
- **Notes:** Proposes two 'novel' metrics: global EMD (with conditioning features in transport cost; compared gen-vs-test against test-vs-train baseline) and per-sample out-of-support uncertainty. Missing-lead R² 0.98-0.99 vs Dower 0.71-0.87. Amplitude-normalised beats, so amplitude fidelity is not evaluated.
- **Takeaway for ECGEN-Eval:** Adopt EMD with real-vs-real (train vs test) reference baseline, and a per-sample out-of-support/novelty score.
- *Extraction source: full-text*
