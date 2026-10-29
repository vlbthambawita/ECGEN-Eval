# rECG: A Guided Diffusion Framework for Remote Electrocardiography Reconstruction from Facial Video
- **ID / Year / Venue:** P122 / 2025 / IEEE IJCB 2025
- **Model & task:** Diffusion (GEDM: 3D-CNN video latent DDPM with fiducial region-aware noise, cross-attention to PhysNet rPPG); facial video → single-lead ECG
- **Losses:** diffusion objective with time- and frequency-domain losses (not detailed)
- **Evaluation:** HR MAE/RMSE; waveform MAE/RMSE/PSNR; Fréchet distance; LF/HF errors and ratio; per-subject STD; Pearson; PTT MAE; cross-dataset test; ablation [fidelity, clinical, robustness]
- **Data:** PFDD (new, 100 subjects, diverse skin tones), MAHNOB-HCI, OBF; leads: 1; fs: 30 Hz (downsampled); length: ~3-beat segments (P onset to third T offset)
- **Notes:** PFDD HR MAE 0.29 bpm, MAE 0.0188, PSNR 21.24 dB, Fréchet 0.12; OBF r 0.923 vs 0.85. ECG at 30 Hz cannot resolve QRS morphology; segmentation and noise masks rely on ground-truth ECG fiducials (leakage risk); subject split undescribed; no skin-tone-stratified results despite the dataset's motivation.
- **Takeaway for ECGEN-Eval:** ECGEN-Eval should warn when the evaluated sampling rate is too low for morphology metrics (e.g. <100-125 Hz) and support subgroup-stratified reporting (e.g. by skin tone/sex) so fairness claims can be checked.
- *Extraction source: full-text*
