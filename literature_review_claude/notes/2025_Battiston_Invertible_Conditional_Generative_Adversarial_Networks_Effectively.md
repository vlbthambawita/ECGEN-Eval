# Invertible Conditional Generative Adversarial Networks to Effectively Generate Myocardial Infarction from Normal ECG
- **ID / Year / Venue:** P095 / 2025 / IEEE EMBC 2025
- **Model & task:** GAN (IcGAN: conditional GAN + encoder inverting real beat to latent; vs CycleGAN with same generator); 12-lead heartbeat style transfer NORM ↔ ASMI ↔ IMI
- **Losses:** cGAN adversarial BCE; encoder L2 latent/label reconstruction
- **Evaluation:** per-lead 90% confidence bands; UMAP overlays; GAN-train / GAN-test; per-lead ST-segment amplitude Hotelling T² CIs [fidelity, diversity, utility-TSTR, clinical, conditional]
- **Data:** PTB-XL subset (NORM/ASMI/IMI, patient-wise split); leads: 12; fs: 100 Hz; length: 0.40 s beats
- **Notes:** IcGAN GAN-test 84% (baseline 90%), GAN-train 73% (baseline 100%) vs CycleGAN 74%/60%. Synthetic ST amplitudes differ by −0.014 to 0.050 mV, below the 0.1 mV STEMI threshold. Same group as P073; no expert review and preservation of patient identity only shown visually.
- **Takeaway for ECGEN-Eval:** Add a per-lead clinical-feature comparison with simultaneous confidence intervals (e.g. ST amplitude from the features module) judged against clinical decision thresholds, and support GAN-train/GAN-test as a paired diversity/fidelity utility metric.
- *Extraction source: full-text*
