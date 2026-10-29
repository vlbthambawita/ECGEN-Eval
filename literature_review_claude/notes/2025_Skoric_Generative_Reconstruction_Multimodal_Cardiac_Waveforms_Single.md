# Generative Reconstruction of Multimodal Cardiac Waveforms From a Single Vibrational Cardiography Sensor
- **ID / Year / Venue:** P087 / 2025 / IEEE Journal of Biomedical and Health Informatics
- **Model & task:** GAN (conditional 1D pix2pix, U-Net + PatchGAN); VCG (SCG+GCG) → ECG, ICG, NIBP, PPG translation
- **Losses:** L1 reconstruction + BCE adversarial
- **Evaluation:** per-subject median Pearson R and MAE; fiducial-point timing MAE/ME (NeuroKit2); per-intervention and window-size stratification; error vs demographics [fidelity, clinical, robustness, fairness]
- **Data:** Private McGill 20-subject multimodal dataset; leads: 1; fs: 200 Hz; length: 2.56 s (up to 20.48 s tested)
- **Notes:** LOSO median ECG R 0.808, MAE 0.309 (z-scored); R-peak timing MAE 6.66 ms, other ECG fiducials 12-28 ms; stable across interventions. Signals amplitude-normalised (amplitudes not recovered); fiducial pairs >250 ms apart discarded.
- **Takeaway for ECGEN-Eval:** For paired translation tasks, add a fiducial-timing metric (matched R/P/Q/S/T peak error in ms, with the match-rejection threshold and discard rate reported) and report per-subject medians plus condition-stratified results.
- *Extraction source: full-text*
