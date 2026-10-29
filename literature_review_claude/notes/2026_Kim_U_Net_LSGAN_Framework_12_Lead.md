# A U-Net Based LSGAN Framework for 12-Lead ECG Synthesis in Wearable IoMT Systems
- **ID / Year / Venue:** P008 / 2026 / IEEE Internet of Things Journal
- **Model & task:** GAN (LSGAN with 1D U-Net generator and 1D PatchGAN discriminator); lead reconstruction from leads I+II to the other 10 leads
- **Losses:** LSGAN least-squares adversarial loss + L1 reconstruction loss (lambda 200)
- **Evaluation:** Per-lead PCC, RMSE, MAE, PRD; R-peak detection rate and R–R interval MAE; ablation of GAN objectives; training-loss curves; params and CPU latency; qualitative overlays [fidelity, clinical, efficiency]
- **Data:** PTB-XL (patient-wise 12000/3000/5000) + PTB Diagnostic; leads: 2 in -> 10 generated; fs: 100 Hz; length: 2.56 s
- **Notes:** Mean PCC 0.905 (PTB 0.888); ablation: no L1 0.0004, L1 only 0.861, standard GAN 0.856, WGAN-GP 0.904. RR MAE 0.0977 s; 4.88 M params, 12.63 ms/segment on CPU. Averaged PCC includes limb leads that are linear combinations of the inputs (Einthoven/Goldberger), which inflates the headline.
- **Takeaway for ECGEN-Eval:** For lead-reconstruction reports, ECGEN-Eval should report per-lead scores and flag leads that are derivable from the inputs (III, aVR, aVL, aVF from I+II), and could add an R–R interval error from the feature extractor as a paired clinical-timing metric.
- *Extraction source: full-text*
