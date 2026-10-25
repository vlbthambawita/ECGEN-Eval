# Leveraging Statistical Shape Priors in GAN-Based ECG Synthesis
- **ID / Year / Venue:** P099 / 2024 / IEEE Access
- **Model & task:** GAN (conditional WGAN-GP generating statistical shape model parameters; 2D shape prior of temporal+amplitude variation; DTW-based k-means; LSTM discriminator); class-cond (heartbeat classes N, V, F); augmentation
- **Losses:** WGAN-GP (Wasserstein adversarial + gradient penalty, lambda=10)
- **Evaluation:** RMSE; MAE; MSE; Earth Mover's Distance (EMD); DTW (ms); downstream precision/recall/F1 of three heartbeat classifiers in 5 augmentation settings; cardiologist visual Turing test (3 cardiologists, real vs synthetic and class identification)
- **Data:** MIT-BIH Arrhythmia (MLII); leads: 1 (MLII); fs: 360; length: single heartbeat, 270 samples (350 ms pre / 400 ms post R-peak)
- **Takeaway for ECGEN-Eval:** Per-class metrics + small cardiologist Turing test; EMD in mV and DTW in ms are interpretable units worth reporting.
- *Extraction source: full-text*
