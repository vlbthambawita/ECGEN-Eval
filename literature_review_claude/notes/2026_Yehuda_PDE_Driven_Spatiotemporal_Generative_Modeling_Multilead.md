# PDE-Driven Spatiotemporal Generative Modeling for Multilead ECG Synthesis
- **ID / Year / Venue:** P111 / 2026 / Proceedings of the AAAI Conference on Artificial Intelligence
- **Model & task:** GAN (PDE-based physics generator, 'PhysioPDE-GAN', reaction-diffusion SA/AV/HP subsystems over lead lattice); class-cond 12-lead beat generation / augmentation
- **Losses:** Non-saturating adversarial loss + coupled PDE residual loss (forward-Euler derivative vs learned response, weighted per SA/AV/HP) + temporal gating loss (Frobenius penalty on activity outside P/PR/QRS-T masks); standard discriminator loss
- **Evaluation:** Downstream classifier specificity at fixed sensitivity on real held-out test set (ResNet and attention-ResNet), real vs real+synthetic augmentation across baselines (DCGAN, WaveGAN, ME-GAN, MultiODE-GAN, SSSD-ECG); 5-fold cross-validated paired t-test; qualitative beat comparison
- **Data:** Georgia 12-Lead ECG Challenge (G12EC); PTB-XL (generalization); leads: 12; fs: 500; length: single heartbeat cycles segmented from 10 s recordings
- **Takeaway for ECGEN-Eval:** Specificity-at-fixed-sensitivity augmentation protocol with paired t-tests is a good utility-evaluation template.
- *Extraction source: full-text*
