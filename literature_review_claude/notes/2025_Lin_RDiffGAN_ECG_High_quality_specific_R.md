# RDiffGAN-ECG: High-quality specific R-peaks conditional ECG generation using denoising diffusion generative adversarial network with state space models
- **ID / Year / Venue:** P121 / 2025 / Biomedical Signal Processing and Control
- **Model & task:** Denoising diffusion GAN (50 steps) with SSSD-ECG-style generator mixing S4 (time step, R-peak) and Mamba (diagnosis) blocks and a JCU discriminator; 12-lead generation conditioned on PTB-XL superclass and an R-peak position/amplitude vector
- **Losses:** Diffusion noise MSE + R-peak loss + JCU least-squares adversarial loss
- **Evaluation:** RMSE, curve Fréchet distance, DTW (overall, per class, CPSC2018), heart-rate statistics, t-SNE, beat quantile bands, discriminator real/fake test, generation time, ablations [fidelity, distribution, clinical, efficiency, conditional]
- **Data:** PTB-XL (5 superclasses) + CPSC2018 NORM; leads: 12 (8 generated); fs: 100 Hz; length: 10 s
- **Notes:** RMSE 0.2245 / FD 5.68 / DTW 68.1 vs SSSD-ECG 0.2803 / 7.77 / 93.2; HR mean 80.1 vs real 79.7; real/fake classifier accuracy 0.525. Paired metrics are computed against the real ECG that supplied the R-peak condition while baselines receive no R peaks, so the comparison is biased; HR agreement is largely by construction.
- **Takeaway for ECGEN-Eval:** When generation is conditioned on fiducials taken from a real record, ECGEN-Eval reports should flag paired mae/dtw scores as conditioning-aligned and compare baselines with unpaired distributional metrics (fd, mmd, nn-based prd) plus heart_rate on held-out conditions.
- *Extraction source: full-text*
