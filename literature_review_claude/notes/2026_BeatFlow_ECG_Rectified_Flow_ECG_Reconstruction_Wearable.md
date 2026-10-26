# BeatFlow-ECG: Rectified Flow for ECG Reconstruction from Indirect Wearable Signals
- **ID / Year / Venue:** P182 / 2026 / arXiv 2610.09052 (preprint, under review)
- **Model & task:** BeatFlow-ECG, a conditional rectified-flow model (conv encoder-decoder + transformer bottleneck, 120 Euler steps) reconstructing single-channel ECG from wrist PPG, IMU motion features and a PPG phase feature.
- **Losses:** Motion-weighted L1 velocity-matching loss plus 0.10 x L1 STFT magnitude loss, with an easy-to-hard motion curriculum.
- **Evaluation:** Paired L1, RMSE, Pearson r, R-peak F1 (100 ms) and HR error under LOSO with 95% CIs and Wilcoxon tests; P/QRS/T regional correlations; motion-stratified error; per-subject tables; NFE/latency; ablations; against UNet1D, AttnSeq, Conditional DDPM-1D and CardioGAN.
- **Data:** PPG-DaLiA and WESAD (public, healthy subjects), filtered, resampled to 125 Hz, per-window z-scored, 10-s windows with 5-s stride.
- **Takeaway for ECGEN-Eval:** Add R-peak F1 with a fixed tolerance, HR error, and P/QRS/T region-wise correlation, and support stratifying any metric by an external covariate (e.g., motion level) with per-subject confidence intervals.
- *Extraction source: full-text*
