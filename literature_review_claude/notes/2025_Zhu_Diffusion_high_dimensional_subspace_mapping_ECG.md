# Diffusion-based high dimensional subspace mapping for ECG generation with structured state space models
- **ID / Year / Venue:** P184 / 2025 / Applied Intelligence
- **Model & task:** Diffusion (DDPM, SSSD-ECG-style S4 layers + patch cross-transformer + multi-scale conv; 71 label-specific embedding subspaces with semi-hard triplet loss); class-conditional 12-lead PTB-XL generation on 71 statements
- **Losses:** DDPM noise-prediction loss + semi-hard triplet loss (1:1)
- **Evaluation:** macro-AUROC of XResNet1d50 under TRTR/TSTR/TRTS/TSTS; ablations; qualitative comparisons vs SSSD-ECG; unblinded three-cardiologist review; parameter count [utility-TSTR, expert, conditional, efficiency]
- **Data:** PTB-XL; leads: 12 (8 generated + 4 derived); fs: 100 Hz; length: 10 s
- **Notes:** TSTR AUROC 0.8612 (SSSD-ECG 0.8402, GANs ~0.58-0.60, real 0.9317); TRTS 0.9576 exceeds real-on-real, hinting at prototypical, low-diversity samples. No fidelity/distribution/diversity or privacy metrics; expert review unscored and unblinded.
- **Takeaway for ECGEN-Eval:** Shows the SSSD-ECG classifier-only protocol in isolation; ECGEN-Eval reports should flag TRTS > TRTR as a possible diversity/mode-collapse signal and pair classifier scores with pr_dist recall, fed and nn_dist to check diversity and memorisation.
- *Extraction source: full-text*
