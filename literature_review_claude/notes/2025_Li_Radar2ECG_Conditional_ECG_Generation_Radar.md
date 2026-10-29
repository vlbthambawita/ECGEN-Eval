# Radar2ECG: Multi-Scale Bottleneck Fusion and Cross-modal Semantic Distillation for Conditional Electrocardiogram Generation from Radar Heart Sound
- **ID / Year / Venue:** P185 / 2025 / IEEE International Conference on Acoustics Speech and Signal Processing
- **Model & task:** Autoencoder-based deterministic translation (1D ResNet-50 encoder + multi-scale fusion bottleneck + 1D DeResNet-50 decoder, teacher-student distillation from a pre-trained ECG autoencoder); radar heart sound -> ECG
- **Losses:** multi-layer cosine feature-distillation + MSE generation loss; AE pre-training
- **Evaluation:** paired RMSE, MAE, cosine similarity, R2; anomaly-detection accuracy on synthetic abnormal inputs; fusion ablation; qualitative plots [fidelity, robustness]
- **Data:** Schellenberger Scidata radar vital-signs dataset (30 healthy subjects, resting); leads: 1; fs: not reported Hz; length: not reported (4,096-sample windows) s
- **Notes:** RMSE 0.0237, cosine 0.987, R2 0.879 vs baselines with negative R2; anomaly detection 99.0%. Overlapping sliding windows split 8:2 without subject separation (likely leakage); abnormal data are artificial; no distribution or clinical metrics.
- **Takeaway for ECGEN-Eval:** For paired cross-modal translation ECGEN-Eval's paired metrics (mae/rmse, psnr) apply directly, but reports should add R2 and timing-based clinical checks (R-peak/HR agreement via the feature extractor) and require subject-disjoint splits to avoid overlapping-window leakage.
- *Extraction source: full-text*
