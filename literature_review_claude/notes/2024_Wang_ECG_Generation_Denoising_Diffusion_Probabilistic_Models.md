# ECG Generation Based on Denoising Diffusion Probabilistic Models
- **ID / Year / Venue:** P056 / 2024 / Computing in cardiology
- **Model & task:** Diffusion (DDPM, Attention U-Net; signal-, STFT-spectrogram- (Griffin-Lim) and wavelet-subband variants); class-cond / augmentation (beats N, LBBB, RBBB, PVC)
- **Losses:** DDPM noise-prediction L2 (epsilon MSE)
- **Evaluation:** DTW; Euclidean distance (ED); Pearson correlation coefficient (PCC); KL divergence (KLD) - all between average synthetic beat and average real beat; visual inspection
- **Data:** MIT-BIH Arrhythmia (MLII; records 102/104/107/217 excluded); leads: 1 (MLII); fs: 360 (beats upsampled to 256 samples); length: ~0.69 (250 samples around R peak)
- **Takeaway for ECGEN-Eval:** Template (mean-beat) PCC/DTW is a useful cheap fidelity check but must be paired with diversity metrics.
- *Extraction source: full-text*
