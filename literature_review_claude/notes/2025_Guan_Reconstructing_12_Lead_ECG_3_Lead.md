# Reconstructing 12-Lead ECG from 3-Lead ECG using Variational Autoencoder to Improve Cardiac Disease Detection of Wearable ECG Devices
- **ID / Year / Venue:** P123 / 2025 / arXiv
- **Model & task:** WearECG: VAE reconstructing 12-lead ECG from 3 wearable-style leads
- **Losses:** MSE reconstruction + beta*KL (1e-4), optional perceptual loss
- **Evaluation:** MSE, MAE, ECGFounder-FID, ECGFounder downstream AUROC, cardiologist Turing test, physician MI reading
- **Data:** MIMIC-IV-ECG; PTB-XL; 500 Hz
- **Takeaway for ECGEN-Eval:** FID on ECGFounder features (as in our FED) plus foundation-model TSTR and Turing test is a complete protocol.
- *Extraction source: full-text*
