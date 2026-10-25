# Classification of imbalanced ECGs through segmentation models and augmented by conditional diffusion model
- **ID / Year / Venue:** P032 / 2024 / PeerJ Computer Science
- **Model & task:** Diffusion (conditional DDPM, U-Net, classifier-free guidance; 1-D reshaped to 2-D) compared with VAE and SMOTE-Tomek; augmentation (class-cond beats for imbalanced arrhythmia classification)
- **Losses:** DDPM L_simple noise-prediction MSE; VAE baseline: reconstruction + KL (ELBO)
- **Evaluation:** Cosine similarity between true and predicted noise on test set (diffusion) / between reconstructed and original (VAE); visual morphology inspection; downstream CNN/transformer classifier Precision, Sensitivity, F1, Accuracy, confusion matrix
- **Data:** MIT-BIH Arrhythmia (AAMI N/S/V/F, records 102/104/107/217 excluded); leads: 1 (MLII); fs: 360; length: single heartbeat segments (length not stated in seconds)
- **Takeaway for ECGEN-Eval:** Illustrates pitfall of using denoising-loss proxies as quality metrics; ECGEN-Eval should promote sample-level distribution metrics instead.
- *Extraction source: full-text*
