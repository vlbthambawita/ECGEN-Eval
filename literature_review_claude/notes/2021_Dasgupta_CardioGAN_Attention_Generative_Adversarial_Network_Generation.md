# CardioGAN: An Attention-based Generative Adversarial Network for Generation of Electrocardiograms
- **ID / Year / Venue:** P175 / 2021 / International Conference on Pattern Recognition (ICPR 2020, held Jan 2021)
- **Model & task:** GAN (WGAN-GP; BiLSTM + attention + LSTM generator, 1D-CNN critic); unconditional single-lead multi-beat ECG window generation
- **Losses:** Wasserstein loss with gradient penalty (λ=10); minimax loss in ablation
- **Evaluation:** PRD, RMSE, discrete Fréchet distance, DTW vs ECGSYN, BiLSTM-GAN and AE/VAE baselines; visual inspection; RR regularity and QT-range check; qualitative anonymity distance check [fidelity, clinical, privacy]
- **Data:** MIT-BIH Arrhythmia; MIT-BIH Normal Sinus Rhythm; leads: 1; fs: 180 (360 Hz subsampled by 2) Hz; length: ~2.8 (512 samples) s
- **Notes:** PRD 38.6, RMSE 0.157, FD 0.606, DTW 4.15 vs BiLSTM-GAN 66.4/0.276/0.756/9.38. Pairing for paired metrics on unconditional output is unspecified; QT 0.36-0.44 s and anonymity claims are given without distributions or numbers. Distinct from Sarkar and Etemad's PPG-to-ECG CardioGAN.
- **Takeaway for ECGEN-Eval:** An early example of using interval checks (RR, QT) as realism evidence; ECGEN-Eval's feature extractor should turn this into a distribution comparison of RR/QT/QTc between real and synthetic sets rather than a single 'within normal range' statement.
- *Extraction source: full-text*
