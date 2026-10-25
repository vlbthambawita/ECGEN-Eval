# Quantum-Refined Latent Diffusion: A Hybrid Generative Framework for Imbalanced ECG Classification
- **ID / Year / Venue:** P120 / 2026 / medRxiv
- **Model & task:** Hybrid (latent diffusion: spectral-guided cVAE + class-conditional latent DDPM with CFG + Quantum Latent Refinement via parameterized quantum circuits); augmentation (class-cond minority beats S, V, F)
- **Losses:** cVAE: MSE + L1 DFT-magnitude spectral loss + β-annealed KL (β→0.05); latent DDPM: noise-prediction MSE; QLR: stay loss ||z_refined − z_raw||² + MMD² (median-heuristic RBF) to real class latent bank; classifier: class-weighted CE
- **Evaluation:** Macro F1 (primary); per-class precision/recall; accuracy; paired t-test over 5 seeds; class-mean waveform RMSD, max |Δ|, cosine similarity; latent distribution drift = multi-bandwidth (5 RBF kernels) MMD²; PCA/KDE latent plots (tags: utility-TSTR;fidelity;distribution)
- **Data:** MIT-BIH Arrhythmia (44 records, AAMI classes; intra-patient temporal 80/10/10 split); leads: 1; fs: 360; length: ~1.08 (389-sample beat window)
- **Notes:** Macro F1 0.747 baseline → up to 0.835 with augmentation. Fidelity measured only on class-mean waveforms (cosine sim misleading for multimodal V class, authors note). Intra-patient temporal split means same patients appear in train and test. MMD used both as training loss and eval metric (circularity risk).
- **Takeaway for ECGEN-Eval:** Use multi-bandwidth MMD rather than single kernel; avoid evaluating with the same metric used as training loss; mean-waveform similarity hides diversity.
- *Extraction source: full-text*
