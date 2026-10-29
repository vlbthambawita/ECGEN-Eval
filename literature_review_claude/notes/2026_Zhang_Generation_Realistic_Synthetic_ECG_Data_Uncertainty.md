# Generation of Realistic Synthetic ECG Data Using Uncertainty-Aware Diffusion Model
- **ID / Year / Venue:** P083 / 2026 / CGI 2025, LNCS 16509
- **Model & task:** Diffusion (DDPM with Dirichlet posterior-network uncertainty guidance via normalizing flows); class-conditional 12-lead generation on PTB-XL superclasses
- **Losses:** DDPM noise L2 + λ·Bayesian posterior-network loss
- **Evaluation:** single-cardiologist blinded authenticity review vs Pulse2Pulse and SSSD-ECG; qualitative per-class case study [expert, fidelity]
- **Data:** PTB-XL; leads: 12; fs: 100 Hz; length: 10 s
- **Notes:** No quantitative metric is reported (no identification rates, no FID/MMD, no downstream utility); superiority claims rest on anecdotal expert comments. Authors concede a remaining gap for training downstream classifiers.
- **Takeaway for ECGEN-Eval:** Illustrates why a standard quantitative report is needed: ECGEN-Eval should make it trivial to add distributional (fd/fed/mmd), clinical-feature and per-class metrics alongside any expert review, and expert studies should report counts and identification rates.
- *Extraction source: full-text*
