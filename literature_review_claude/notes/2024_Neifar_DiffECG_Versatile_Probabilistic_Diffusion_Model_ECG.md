# DiffECG: A Versatile Probabilistic Diffusion Model for ECG Signals Synthesis
- **ID / Year / Venue:** P047 / 2024 / IEEE/ACIS International Conference on Software Engineering Research, Management and Applications (SERA)
- **Model & task:** DiffECG: spectrogram DDPM unified for beat generation, imputation, forecasting
- **Losses:** DDPM epsilon loss + MSE regression term
- **Evaluation:** RMSE, MAE, FID, DTW, EMD, MMD per class; augmentation accuracy/F1
- **Data:** MIT-BIH MLII, N/V/F beats, 360 Hz
- **Takeaway for ECGEN-Eval:** EMD and per-class reporting are cheap additions; FID without a specified extractor is not comparable across papers.
- *Extraction source: full-text*
