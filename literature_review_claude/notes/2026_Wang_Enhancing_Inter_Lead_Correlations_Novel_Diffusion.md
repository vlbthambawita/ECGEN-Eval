# Enhancing Inter-Lead Correlations: A Novel Diffusion GAN Framework for 12-Lead ECG Generation
- **ID / Year / Venue:** P071 / 2026 / ICASSP 2026
- **Model & task:** Hybrid Diffusion-GAN (EDIFFGAN: denoising-diffusion GAN generating 9 electrode signals, electrode superposition module derives 12 leads; frozen ResNet34 classifier loss); class-conditional 12-lead heartbeat generation on PTB-XL superclasses
- **Losses:** diffusion-GAN adversarial loss on noisy transition pairs + cross-entropy classification loss
- **Evaluation:** proposed ECGLS (DTW-based limb-lead Einthoven/Goldberger consistency); FID; generation time; augmentation AUROC/Prec/Recall/F1; ECGLS sensitivity to noise [fidelity, clinical, utility-TSTR, efficiency]
- **Data:** PTB-XL; leads: 12; fs: 500 Hz; length: 1.024 s (512-sample R-centred beats)
- **Notes:** ECGLS 1.32e-5 vs 4.85-155.44 for baselines; FID 2.12 vs 5.14-33.82; 2.63 s vs 2606.78 s (DDPM-2D) for 20k samples; augmentation F1 0.717 vs 0.617. ECGLS is essentially zero by construction for the proposed model (leads derived from electrodes), covers only limb leads, and the FID embedding network is unspecified.
- **Takeaway for ECGEN-Eval:** Add an inter-lead consistency metric checking Einthoven (II = I + III) and Goldberger (aVR/aVL/aVF) relations for 12-lead outputs (plain residual plus optional DTW), and note in the report that architectures deriving leads physically score ~0 trivially.
- *Extraction source: full-text*
