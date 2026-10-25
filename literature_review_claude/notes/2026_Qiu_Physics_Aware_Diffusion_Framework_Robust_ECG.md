# A Physics-Aware Diffusion Framework for Robust ECG Synthesis Using Mesoscopic Lattice Boltzmann Constraints
- **ID / Year / Venue:** P007 / 2026 / Biology
- **Model & task:** Diffusion (conditional DDPM with Lattice-Boltzmann physics encoder, 'PhysDiff-LBM'); PPG2ECG
- **Losses:** Weighted sum: DDPM noise-prediction MSE (L_diff) + BCE topology loss vs ground-truth QRS mask (L_reg) + hemodynamic physics-consistency loss (L2 between temporal derivative of Tweedie-estimated x0 and LBM momentum flux, L_phys)
- **Evaluation:** RMSE; HR-MAE (heart rate via Pan-Tompkins); Fréchet Distance on raw signal windows; downstream AF / arrhythmia classification Accuracy, Precision, Recall/Sensitivity, Specificity, F1, AUC with 95% bootstrap CIs, paired permutation and DeLong tests
- **Data:** MIMIC-III Waveform DB; VitalDB (OOD generalization); MIMIC PERform AF (downstream AF classification); PhysioNet Challenge 2015 (5-class arrhythmia downstream); leads: 1 (single-lead ECG from single PPG); fs: 128 (resampled); length: 4 (non-overlapping windows)
- **Takeaway for ECGEN-Eval:** HR-MAE (Pan-Tompkins HR error) and downstream classifier comparison with bootstrap CIs/DeLong tests are cheap, clinically meaningful additions.
- *Extraction source: full-text*
