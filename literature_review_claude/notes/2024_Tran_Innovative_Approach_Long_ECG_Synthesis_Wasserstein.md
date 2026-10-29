# An Innovative Approach for Long ECG Synthesis with Wasserstein GAN Model
- **ID / Year / Venue:** P017 / 2024 / Lecture Notes in Computer Science (ICCSA 2024)
- **Model & task:** DCGAN trained with WGAN-GP on binary line-plot images of ECG (beats 128x128; 10 s as two 5 s rows in 240x480), signal recovered from image by column search; class-wise beat (N/S/V/F) and 10 s rhythm (NSR/VT/SVT) synthesis for augmentation
- **Losses:** WGAN-GP (lambda 10)
- **Evaluation:** MSE, RMSE/NRMSE, SSIM, cross-correlation on beats; CNN beat classification (train on real+synthetic, test on synthetic); visual comparison with Pan-Tompkins R peaks for 10 s signals; generation time [fidelity, utility-TSTR, efficiency]
- **Data:** MIT-BIH Arrhythmia (DS1/DS2), European ST-T, Chapman; leads: 1; fs: 250 Hz; length: single beats and 10 s
- **Notes:** Beats: MSE 0.00179, RMSE 0.0237, SSIM 0.9978, CC 0.9546; augmentation ACC 99.31→99.78. 10 s synthesis evaluated only qualitatively; pairing for MSE/SSIM undefined; binary-image representation discards true amplitude.
- **Takeaway for ECGEN-Eval:** Long-ECG (10 s rhythm) papers still lack quantitative evaluation, so ECGEN-Eval's heart_rate, hrv and feature-extractor RR distributions should be promoted as the standard rhythm-level metrics, with nearest-neighbour pairing made explicit for mse/ssim-style scores.
- *Extraction source: full-text*
