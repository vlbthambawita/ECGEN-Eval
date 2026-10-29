# Deep Learning Driven Physiological Signal Generation: An Improved DDIM-Based ECG Synthesis Framework
- **ID / Year / Venue:** P044 / 2025 / International Congress on Image and Signal Processing, BioMedical Engineering and Informatics (CISP-BMEI)
- **Model & task:** Diffusion (DDIM variant 'AD-DIM' with ShiftNet structure-aware forward encoder, shifted-diffusion offset, lightweight MSCnet/BConv reverse network); single-lead AF-class augmentation for imbalanced AF detection
- **Losses:** diffusion denoising objective with SNR-modulated weighting (not formally given); cross-entropy for the downstream classifier
- **Evaluation:** downstream Acc/Sen/Spe/F1 (CGLNet) at 5:1, 3:1, 1:1 class ratios; Acc/F1 vs forward noise level; DTW to random real templates (figure); params/GFLOPs; qualitative P/T-wave comparison [utility-TSTR, fidelity, efficiency]
- **Data:** MIT-BIH AFDB, private SPHDB wearable 24 h AF, CPSC2018, PTB-XL; leads: 1; fs: not reported Hz; length: not reported s
- **Notes:** 1:1 balancing gives AFDB F1 99.48, CPSC2018 98.10, PTB-XL 91.89; vs DDIM 97.52 and GAN 91.34 F1 with 0.08 M params. Conclusion cites SSIM > 0.92, FID-ECG 12.7, 62.4% SNR gain, 42% DTW reduction and MIT-BIH experiments that do not appear in the results; template text left in the methods. The P/T comparison splices original segments into generated signals (paired local error). Treat as low-confidence evidence.
- **Takeaway for ECGEN-Eval:** Segment-wise (P-wave / T-wave window) fidelity is a useful idea for the clinical feature extractor, but this paper shows why ECGEN-Eval reports must state pairing, sample counts and embedding network for every number, since unsupported headline metrics (FID-ECG, SSIM) cannot be reproduced.
- *Extraction source: full-text*
