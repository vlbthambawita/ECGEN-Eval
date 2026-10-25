# Generating Realistic Multi-Beat ECG Signals
- **ID / Year / Venue:** P080 / 2025 / arXiv
- **Model & task:** Hybrid (beat-level time-series Diffusion with prompt bases + multivariate feature-sequence generator + feature-guided beat matching/stitching); unconditional (long-form multi-beat), class-cond (normal/abnormal beats); augmentation
- **Losses:** not reported
- **Evaluation:** Beat level: DTW, Frechet distance, Euclidean distance, RMSE, MAE, MSE, PRD between average beats; average KL, JS divergence, MMD, Wasserstein, KS statistic, mean/variance/skewness differences. Features: per-feature KL, MMD, Wasserstein, KS, mean difference; feature correlation matrices; density-difference heatmap. Utility: TSTR accuracy/precision/recall/F1 (SVM, Balanced SVM, Decision Tree, Naive Bayes, and others); R-amplitude matching rate
- **Data:** MIT-BIH Supraventricular Arrhythmia Database (main); MIT-BIH Arrhythmia (additional test); leads: 1; fs: 128; length: single beats ~100-200 samples; long-form sequences (e.g., 100 beats)
- **Takeaway for ECGEN-Eval:** Compare inter-beat feature distributions (KS/Wasserstein per interval) and feature-correlation matrices; avoid average-beat-only metrics.
- *Extraction source: full-text*
