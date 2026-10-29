# ECG-DPM: Electrocardiogram Generation via a Spectrogram-based Diffusion Probabilistic Model
- **ID / Year / Venue:** P063 / 2024 / IEEE Smart World Congress (SWC)
- **Model & task:** Diffusion (DDPM with 2-D UNet on 3-channel real/imaginary/magnitude STFT spectrograms, inverse STFT to waveform); class-conditional single-lead normal/AF generation, 5 s and 30 s
- **Losses:** MSE noise-prediction loss
- **Evaluation:** pre-trained AF-classifier precision/recall on synthetic; FID on InceptionV3 embeddings of power spectrograms; baseline-drift slope; visual inspection [fidelity, distribution, conditional]
- **Data:** PhysioNet/CinC 2017 (normal + AF); leads: 1; fs: 300 Hz; length: 5 and 30 s (spectrogram cropped to 64 bins, about 37 Hz low-pass)
- **Notes:** 30 s: precision 0.593, recall 0.686, FID 24.3, slope 8.8e-4 vs 1D-Diffusion 0.527/0.592/38.8/2.35e-3. Sampling starts from real training spectrograms noised for Λ=100-200 steps (SDEdit-style), so outputs are partly derived from real records with no memorisation check; precision/recall here are classifier scores, and only 150 samples per class are evaluated.
- **Takeaway for ECGEN-Eval:** Add a baseline-wander/drift statistic (e.g. slope of a fitted baseline) as a cheap signal-level check, and caveat that FID from ImageNet InceptionV3 on spectrograms is not comparable to ECG-specific fed; nn_dist should be run for models that sample from noised real data.
- *Extraction source: full-text*
