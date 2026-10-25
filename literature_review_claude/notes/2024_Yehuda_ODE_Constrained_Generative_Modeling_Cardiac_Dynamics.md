# ODE-Constrained Generative Modeling of Cardiac Dynamics for 12-Lead ECG Synthesis
- **ID / Year / Venue:** P107 / 2024 / arXiv
- **Model & task:** GAN (MultiODE-GAN: WaveGAN-based WGAN with ODE (McSharry EDM) physics constraints); task: class-cond (beat-level 12-lead, per abnormality) / augmentation
- **Losses:** Wasserstein adversarial loss + λ_EUL·Euler Loss = intra-lead Euler loss (ODE residual vs McSharry EDM) + inter-lead Euler loss (Einthoven/derivative consistency), weighting δ=0.6
- **Evaluation:** Downstream ResNet classifier specificity at fixed sensitivity (real vs real+synthetic, paired t-test); AUROC; AUPRC; inter-lead MSE (Einthoven law consistency); KL divergence and MMD in pretrained ResNet feature space; LVSD detection vs six cardiologists (tags: utility-TSTR; distribution; clinical)
- **Data:** Georgia 12-Lead ECG Challenge (G12EC); PTB-XL; private LVSD dataset (real-world evaluation); leads: 12; fs: 500 Hz; length: single heartbeat (L=300 samples, NeuroKit2 segmentation of 10-s records) s
- **Notes:** Inter-lead Einthoven MSE is a physiology-consistency metric. Baselines: SimGAN-extended, SSSD-ECG. KL<0.5 and MMD<0.01 for all abnormalities. Augmentation-only (TRTR vs TR+S) evaluation; no TSTR.
- **Takeaway for ECGEN-Eval:** Add an Einthoven/Goldberger inter-lead consistency metric (e.g., MSE of I - (II - III)) for 12-lead synthetic data.
- *Extraction source: full-text*
