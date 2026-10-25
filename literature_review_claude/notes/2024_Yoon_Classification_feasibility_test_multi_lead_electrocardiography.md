# Classification feasibility test on multi-lead electrocardiography signals generated from single-lead electrocardiography signals
- **ID / Year / Venue:** P030 / 2024 / Scientific Reports
- **Model & task:** GAN (pix2pix conditional GAN, U-Net generator, 1-D; 11 per-lead models); task: lead-reconstruction
- **Losses:** cGAN adversarial loss + L1 reconstruction loss (pix2pix objective G* = argmin max L_cGAN + L_L1)
- **Evaluation:** Downstream ResNet classification precision; recall; F1-score; accuracy; ROC/AUC (6 classes: normal, AF, LBBB, RBBB, LVH, RVH) comparing generated 12-lead vs real 12-lead vs real lead I; Einthoven-derived lead ablations (tags: utility-TSTR; clinical)
- **Data:** Asan Medical Center MUSE database (training, ~4M records); PTB-XL (external, classification); leads: 1 -> 12 (lead I input); fs: 500 Hz; length: 2.5 segments (1250 samples) from 10 s records s
- **Notes:** Generation fidelity (FD, MSE) evaluated in prior work; here utility only. Surprising: generated 12-lead F1 0.81 > real 12-lead 0.70 on PTB-XL; authors suggest FD/MSE plus Turing test needed. Mixed-in Einthoven-formula leads gave no significant difference.
- **Takeaway for ECGEN-Eval:** Utility comparison vs. the single-lead input baseline is a useful 'information gain' check for lead-reconstruction models.
- *Extraction source: full-text*
