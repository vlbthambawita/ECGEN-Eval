# A performance analysis of convolutional autoencoder modified WaveGAN architectures for realistic 12 lead electrocardiogram synthesis
- **ID / Year / Venue:** P005 / 2025 / Scientific Reports
- **Model & task:** GAN (WaveGAN/WGAN-style with convolutional-autoencoder feature extractor; CAE-WaveGAN); unconditional
- **Losses:** CAE reconstruction loss (MSE or BCE); Wasserstein adversarial loss for discriminator/generator (WGAN-style critic loss)
- **Evaluation:** PSNR; SSIM; Morphology Similarity (MorphSim); Spectral Similarity (SpecSim); standard deviation of generator training/validation loss (stability); epoch time
- **Data:** CODE-15% (training/ablation); PTB-XL (visual comparison only); leads: 12; fs: 400; length: ~10 (4096 samples, 7 s and 10 s records zero-padded)
- **Takeaway for ECGEN-Eval:** MorphSim/SpecSim are cheap per-sample sanity metrics, but avoid post-hoc quality filtering and absolute PSNR/SSIM on unpaired generations.
- *Extraction source: full-text*
