# Compact Latent Manifold Translation: A Parameter-Efficient Foundation Model for Cross-Modal and Cross-Frequency Physiological Signal Synthesis
- **ID / Year / Venue:** P035 / 2026 / arXiv
- **Model & task:** CLMT: RVQ discrete latent foundation model for PPG->ECG translation and 4x ECG super-resolution
- **Losses:** L1 + cosine + gradient-L1 shape-aware loss + VQ commitment (stage 1); latent MSE (stage 2)
- **Evaluation:** RMSE, MAE, R-peak F1, Frechet Distance, Pearson, PSD-RMSE
- **Data:** Unnamed ECG/PPG datasets; 100 Hz target
- **Takeaway for ECGEN-Eval:** R-peak detection F1 between real and generated signals is a simple landmark-fidelity metric; PSD-RMSE complements PSD JS divergence.
- *Extraction source: full-text*
