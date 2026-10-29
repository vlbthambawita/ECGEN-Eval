# Text-to-ECG: a Framework to Generate 12-Lead ECG from Text Reports
- **ID / Year / Venue:** P144 / 2025 / IEEE EMBC (Annual International Conference of the IEEE Engineering in Medicine and Biology Society)
- **Model & task:** GAN (conditional WGAN-GP; 1D upsample-conv generator, 2D-conv critic; frozen Bio_ClinicalBERT text embedding); text-conditional 12-lead single-heartbeat synthesis for NORM, IMI, ASMI, LAFB, LVH
- **Losses:** WGAN-GP critic loss (lambda=10) + generator Wasserstein loss; instance noise on critic inputs
- **Evaluation:** UMAP + KDE overlap; GAN-train / GAN-test per-class F1 and accuracy; per-lead 90% confidence-band IoU; visual comparison [fidelity, distribution, diversity, utility-TSTR, conditional]
- **Data:** PTB-XL (100 Hz, 29,391 balanced beats); leads: 12; fs: 100 Hz; length: 0.5 s
- **Notes:** GAN-train accuracy 0.92 synthetic vs 0.60 real (low diversity); GAN-test 0.84 real vs 0.72 synthetic; band IoU 0.73-0.80. ASMI beats map onto IMI region. No expert evaluation; text conditioning reduces to 5 class labels with ~25 paraphrases each.
- **Takeaway for ECGEN-Eval:** The per-lead 90% confidence-band IoU is a cheap, interpretable class-conditional envelope-overlap metric that ECGEN-Eval could add for aligned beats, alongside reporting GAN-train/GAN-test (TSTR/TRTS) pairs to separate diversity from fidelity.
- *Extraction source: full-text*
