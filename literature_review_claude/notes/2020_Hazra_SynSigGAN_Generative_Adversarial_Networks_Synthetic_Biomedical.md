# SynSigGAN: Generative Adversarial Networks for Synthetic Biomedical Signal Generation
- **ID / Year / Venue:** P165 / 2020 / Biology
- **Model & task:** GAN (SynSigGAN: bidirectional Grid-LSTM generator + CNN discriminator); unconditional / class-wise (per-annotation segments) synthesis of ECG, EEG, EMG, PPG
- **Losses:** standard GAN generator/discriminator adversarial losses (DWT-based denoising in preprocessing evaluated with SNR, RMSE, PRD)
- **Evaluation:** Pearson correlation coefficient (mean); MAE; RMSE; PRD; Fréchet distance (discrete curve distance); classification accuracy of other models on synthetic signals; SNR/RMSE/PRD for preprocessing denoising [fidelity; utility-TSTR]
- **Data:** MIT-BIH Arrhythmia (ECG); Siena Scalp EEG; Sleep-EDF (EMG); BIDMC PPG and Respiration; leads: not reported (MIT-BIH has MLII + one precordial); fs: 360 (MIT-BIH) Hz; length: not reported (beat segments based on median RR) s
- **Notes:** ECG: PCC 0.9991, MAE 0.218, RMSE 0.126, PRD 6.343, FD 0.936; baselines PRD 68-119. Established the PCC/MAE/RMSE/PRD/FD 'paired' metric suite later copied widely; pairing of generated vs original signals is not clearly defined for unconditional generation.
- **Takeaway for ECGEN-Eval:** Classic metric suite origin; ECGEN-Eval should implement curve FD and PRD with explicit nearest-neighbour pairing and document the caveat.
- *Extraction source: full-text*
