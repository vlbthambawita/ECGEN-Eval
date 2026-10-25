# CLEP-GAN: An Innovative Approach to Subject-Independent ECG Reconstruction from PPG Signals
- **ID / Year / Venue:** P034 / 2025 / arXiv
- **Model & task:** GAN (CLEP-GAN: Attention U-Net generators + contrastive learning + dual time/frequency discriminators; CLEP-VQGAN variant with VQ-VAE); PPG2ECG (subject-independent)
- **Losses:** NT-Xent contrastive loss (PPG->ECG) + reconstruction losses Lp2p, Le2e, Lp2e + VQ dictionary & commitment losses (VQGAN variant) + adversarial losses from time-domain and STFT-spectrogram frequency-domain discriminators; Ltotal = 30·Lgen + 3·Lt + 1·Lf
- **Evaluation:** RR-interval distribution: relative Histogram Intersection (rHI), relative RMSE, relative EMD, KL divergence, two-sample KS test; waveform RMSE; MAE of heart rate (MAE_HR); HRV (mean RR, SDNN of RR) GT vs reconstruction; Fréchet Distance in feature space; MFLOPs, MParams, inference time (tags: fidelity;distribution;clinical;efficiency)
- **Data:** BIDMC PPG and Respiration; CapnoBase TBME RR (resampled 300->125 Hz); ODE-based synthetic ECG-PPG dataset (RSR, SA, AFib); leads: 1; fs: 125; length: ~4 (512 samples)
- **Notes:** RR-interval histogram metrics with fixed bin width used to validate the synthetic ODE dataset. Analyses effects of sex/age on reconstruction; warns against indiscriminate dataset augmentation. T-wave reconstruction remains inconsistent. Baselines: CardioGAN, QRS-ED, RDDM.
- **Takeaway for ECGEN-Eval:** RR-interval distribution comparison with several divergences (HI, EMD, KL, KS) is a simple rhythm-fidelity metric family worth adding.
- *Extraction source: full-text*
