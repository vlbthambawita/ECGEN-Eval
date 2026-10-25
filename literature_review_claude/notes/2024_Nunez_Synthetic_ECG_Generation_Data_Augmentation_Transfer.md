# Synthetic ECG Generation for Data Augmentation and Transfer Learning in Arrhythmia Classification
- **ID / Year / Venue:** P139 / 2024 / arXiv
- **Model & task:** Diffusion (DiffWave/SSSD-ECG; Time-Diffusion = HF Diffusers Unet1D conditional) + VQ-VAE/MaskGIT (Time-VQVAE, TimeVQVAE); class-cond (rhythm classes); augmentation; transfer learning
- **Losses:** not detailed; uses original models' objectives (DiffWave variational bound / diffusion noise prediction; VQ-VAE + MaskGIT prior)
- **Evaluation:** t-SNE, UMAP, PaCMAP visualisations; 2-sample classifier test (real-vs-synthetic accuracy, 50% ideal); MMD (RBF); TrRTeR, TrSTeS, TrSTeR (TSTR), TrRTeS (TRTS), TrRSTeR (augmentation) with accuracy, precision, recall, F1, ROC AUC (n=25 repeats); fine-tuning transferability with 20-80% real data (tags: distribution;utility-TSTR)
- **Data:** PTB-XL; Chapman-Shaoxing; merged PTB-XL+Chapman (7 rhythm classes: SBRAD, SR, AFIB, STACH, AFLT, SARRH, SVTAC); leads: 12; fs: not reported (datasets at 100/500 Hz); length: 10
- **Notes:** Key criticism: MMD and t-SNE/UMAP visualisations failed to distinguish synthetic from real, while classifier-based tests (2-sample test, TSTR/TRTS) revealed clear differences. Augmentation gains negligible per dataset, positive on merged set. Time-VQVAE best for fine-tuning but still below real-only.
- **Takeaway for ECGEN-Eval:** Add a classifier two-sample test (C2ST) and full TrRTeR/TSTR/TRTS/TrRSTeR matrix; MMD alone is underpowered.
- *Extraction source: full-text*
