# Translation from Wearable PPG to 12-Lead ECG
- **ID / Year / Venue:** P180 / 2026 / Smart Health (arXiv 2509.25480 v1; published as P2Es)
- **Model & task:** P2Es, a diffusion model that translates PPG into 12-lead ECG (2-s windows, 125 Hz), with a frequency-blur plus QRS-adaptive temporal-noise forward process, multi-scale reverse process with frequency deblurring, 50-step DDIM sampling, and demographic-aware affinity matrices (KNN clustering + contrastive assignment) as conditioning.
- **Losses:** Weighted sum of inter-lead difference L2, Fourier-domain L2, electrical-axis L2, and a signal-alignment loss (R-peak position, peak-to-peak amplitude, heart-rate difference); contrastive loss for the GroupFinder module.
- **Evaluation:** Paired MSE, DTW, residual variance, KL of ECG feature distributions, marginal Wasserstein, electrical-axis similarity S_theta (overall/chest/limb) against single-lead-per-lead, two-stage and Lead-I upper-bound baselines; MI/SVT/VT diagnosis from generated ECG (sensitivity/specificity/accuracy/precision); ablation; MIMIC-III/IV cross-dataset test; on-device latency.
- **Data:** MIMIC-II (clustering), MIMIC-III and MIMIC-IV (paired PPG + 12-lead ECG), resampled to 125 Hz, subject-wise z-scored, 2-s windows, 80/20 patient split.
- **Takeaway for ECGEN-Eval:** Add an electrical-axis similarity metric (from leads I and II) and report every metric split into limb vs chest lead groups for multi-lead generators.
- *Extraction source: full-text*
