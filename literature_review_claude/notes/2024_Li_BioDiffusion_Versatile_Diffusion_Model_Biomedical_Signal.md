# BioDiffusion: A Versatile Diffusion Model for Biomedical Signal Synthesis
- **ID / Year / Venue:** P177 / 2024 / Bioengineering
- **Model & task:** Diffusion (U-Net DDPM, unconditional / label-conditional / signal-conditional; 'BioDiffusion'); unconditional; class-cond; augmentation; also denoising, imputation, super-resolution
- **Losses:** Diffusion denoising loss with L1 norm (cosine noise schedule, 1000 steps)
- **Evaluation:** Wavelet coherence; Discriminative score (2-layer LSTM real-vs-synthetic classifier error, TimeGAN-style); UMAP projections; visual inspection; downstream 1D-CNN per-class F1 / precision / recall on MIT-BIH with synthetic augmentation
- **Data:** MIT-BIH Arrhythmia (5-class beat version at 125 Hz); UniMiB SHAR (accelerometer); simulated shapes dataset; leads: 1; fs: 125; length: ~1.15 (144 samples)
- **Takeaway for ECGEN-Eval:** Wavelet coherence and TimeGAN discriminative score are candidate additions to ECGEN-Eval.
- *Extraction source: full-text*
