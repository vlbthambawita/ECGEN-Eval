# MorphDiff-ECG: A Diffusion Model for Multimodal Feature Fusion of ECG Signals
- **ID / Year / Venue:** P105 / 2026 / IEEE Transactions on Biomedical Engineering
- **Model & task:** Diffusion (DDPM with trend/periodic/morphology decoupling branches + SE-attention fusion, classifier-guided conditioning); class-conditional single-lead beat/segment generation on MIT-BIH, CPSC2020, CPSC2018
- **Losses:** time-domain L1/L2 + CWT wavelet-coefficient loss + morphological opening/closing envelope loss, timestep-reweighted
- **Evaluation:** PRD; TS2Vec Fréchet distance; RMSE; MAE; Pearson; ablation; sensitivity; PCA; CWT maps; compute cost [fidelity, distribution, efficiency]
- **Data:** MIT-BIH, CPSC2020, CPSC2018; leads: 1; fs: 360 Hz; length: ~0.83 s (300 samples)
- **Notes:** MIT-BIH PRD 53.965 vs 55.048 (CECG-GAN), FD 0.738 (MC-WGAN 0.644 better), RMSE 0.207, MAE 0.165; Pearson 0.92-0.99 across datasets. Paired metrics treat generation as reconstruction; PRD scales are inconsistent across tables and the abstract mislabels the dataset; no clinical-interval, expert or downstream utility checks; reference list contains unrelated entries.
- **Takeaway for ECGEN-Eval:** Uses an FD in TS2Vec embedding space, a candidate generic-encoder backbone for fd/fed alongside ECG foundation models; ECGEN-Eval reports should state whether PRD/RMSE/MAE are paired or nearest-neighbour and the PRD scale (fraction vs %), since mixing them makes comparisons like this one meaningless.
- *Extraction source: full-text*
