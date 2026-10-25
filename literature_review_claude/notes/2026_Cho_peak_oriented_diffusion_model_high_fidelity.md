# A peak-oriented diffusion model for high-fidelity electrocardiogram reconstruction from photoplethysmogram: development and usability study
- **ID / Year / Venue:** P004 / 2026 / BioData mining
- **Model & task:** Diffusion (conditional DDPM, 1-D U-Net with self-attention + MLP R-peak predictor on bottleneck); task: PPG2ECG
- **Losses:** DDPM noise-prediction MSE (λ1=1) + L2 R-peak position prediction loss (λ2=1); cosine schedule, T=300
- **Evaluation:** RMSE; Fréchet distance (FD); duration RMSE of P-wave, PR, QRS, QT, T-wave (ms, DWT delineation); peak timing RMSE for P/Q/R/S/T peaks; peak amplitude RMSE; AF detection accuracy/precision/recall/F1 (ResNet-50 trained on real ECG only, tested on reconstructed); HR estimation Bland-Altman mean difference; KS, Kruskal-Wallis, Mann-Whitney with Bonferroni for noise robustness (tags: fidelity; distribution; clinical; utility-TSTR)
- **Data:** MIMIC-III Waveform Matched Subset (+ MIMIC-III Clinical DB for CVD/AF labels); WESAD; PPG-DaLiA (cross-dataset); leads: 1; fs: 128 (resampled from 125/700/64) Hz; length: 4 (512 samples) s
- **Notes:** Argues RMSE/FD ignore short PQRST components and adds per-wave duration/peak-timing RMSE. Results: RMSE 0.220, FD 6.456, AF F1 0.925, HR bias -0.077 bpm; R-peak timing RMSE 19.7 ms. Robustness tested with white noise and motion artifacts; ~60M segments from 5,888 patients.
- **Takeaway for ECGEN-Eval:** Per-fiducial timing/amplitude RMSE (P/Q/R/S/T) and interval-duration errors are a cheap clinically-anchored complement to RMSE/FD for paired tasks.
- *Extraction source: full-text*
