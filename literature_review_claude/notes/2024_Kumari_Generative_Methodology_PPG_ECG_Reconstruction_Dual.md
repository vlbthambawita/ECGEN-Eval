# A Generative Methodology for PPG to ECG Reconstruction Based on Dual-Critic Approach
- **ID / Year / Venue:** P002 / 2024 / Computing in cardiology
- **Model & task:** Dual-critic WGAN-GP (LDGAN) for PPG-to-ECG reconstruction
- **Losses:** WGAN loss on time-domain critic + WGAN loss on DWT-domain critic + gradient penalty
- **Evaluation:** RMSE, PRD, heart-rate MAE; edge-device timing
- **Data:** BIDMC, lead II, 128 Hz, 4 s windows
- **Takeaway for ECGEN-Eval:** Heart-rate MAE between paired real/generated ECG is a cheap clinical check; wavelet-domain comparison could complement PSD.
- *Extraction source: full-text*
