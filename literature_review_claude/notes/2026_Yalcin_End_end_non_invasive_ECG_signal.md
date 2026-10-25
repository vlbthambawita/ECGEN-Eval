# End-to-end non-invasive ECG signal generation from PPG signal: a self-supervised learning approach
- **ID / Year / Venue:** P069 / 2026 / Frontiers in Physiology
- **Model & task:** GAN (WGAN-GP with Transformer-based generator/discriminator; self-supervised pretraining of discriminator via signal-transformation recognition); PPG2ECG
- **Losses:** WGAN-GP adversarial (Wasserstein + gradient penalty, lambda tuned); self-supervised pretext loss: six-way signal-transformation recognition (noise, scaling, temporal inversion, permutation, negation, time-warping)
- **Evaluation:** Frechet Distance (discrete curve FD); RMSE (mV); Pearson correlation; MAE of heart rate (MAEHR, generated ECG vs PPG); MMD^2 and squared Energy Distance with permutation-test p-values on embeddings; t-SNE; AF detection accuracy/precision/recall/F1 with varying synthetic proportions
- **Data:** Who is Alyx? (VR dataset, ECG 130 Hz / Empatica PPG 64 Hz); MIMIC III matched waveform (125 Hz); MIMIC PERform AF (AF detection); pretraining: BIDMC, CapnoBase, WESAD; leads: 1; fs: 130 (all resampled); length: windows of 4-160 s (best 64 s Who is Alyx?, 96 s MIMIC III); 30 s for AF task
- **Takeaway for ECGEN-Eval:** Adopt permutation-test p-values for MMD/energy distance and HR-error (MAEHR); disambiguate curve-FD vs Gaussian FD in naming.
- *Extraction source: full-text*
