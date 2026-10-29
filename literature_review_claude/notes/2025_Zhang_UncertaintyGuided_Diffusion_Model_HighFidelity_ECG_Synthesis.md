# Uncertainty‐Guided Diffusion Model for High‐Fidelity ECG Synthesis and Classification
- **ID / Year / Venue:** P155 / 2025 / Expert Systems
- **Model & task:** DDPM (U-Net, cosine schedule, 500 steps) whose conditioning is produced by a Dirichlet posterior network (uncertainty guidance); PTB-XL statement-conditioned 12-lead synthesis
- **Losses:** 0.6 x epsilon-MSE + 0.3 x Posterior-Network Bayesian loss + 0.1 x KL to Dirichlet prior
- **Evaluation:** KL; marginal distribution difference; skewness difference; DTW; autocorrelation difference; proposed Shapley-style per-lead sample-level fidelity; one-cardiologist blinded test; median-beat plots; PR curves and real-vs-synthetic classifier Se/Sp/F1; t-SNE; ablation; inference time [distribution, fidelity, expert, utility-TSTR, diversity, efficiency]
- **Data:** PTB-XL; leads: 12; fs: 100 Hz; length: 10 s
- **Notes:** KL 0.89, MDD 31.04, SD 0.73 (SSSD 0.93/35.95/0.85); DTW 2.127 vs real-vs-real 2.009 (SSSD 6.363); ACD 0.723 vs 0.718; without uncertainty KL 1.24, DTW 3.98. Classical-classifier F1 on synthetic within a few points of real. The sample-level Shapley metric is defined but never reported; expert test uses 4 ECGs and 1 cardiologist; references and the conditioning description are partly inconsistent.
- **Takeaway for ECGEN-Eval:** Adopt the practice of reporting every metric next to a real-vs-real reference (as done here for DTW and ACD), and consider adding cheap time-series statistics (marginal-histogram difference, skewness difference, autocorrelation difference) as distribution metrics.
- *Extraction source: full-text*
