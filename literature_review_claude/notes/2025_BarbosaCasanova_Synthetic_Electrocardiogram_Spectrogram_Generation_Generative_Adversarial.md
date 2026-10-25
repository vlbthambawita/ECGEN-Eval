# Synthetic Electrocardiogram Spectrogram Generation Using Generative Adversarial Network‐Based Models: A Comparative Study
- **ID / Year / Venue:** P142 / 2025 / Advanced Intelligent Systems
- **Model & task:** GAN (DCGAN, conditional GAN, WGAN-GP) on 2-D spectrogram images; augmentation (class-cond normal/abnormal STFT spectrograms)
- **Losses:** DCGAN: binary cross-entropy adversarial; CGAN: conditional cross-entropy adversarial; WGAN-GP: Wasserstein critic loss + lambda gradient penalty
- **Evaluation:** FID (Inception-V3 'pre-aux' 768-d layer via pytorch-fid); intra-class SSIM diversity (average/max/min pairwise SSIM among generated, values near 1 = mode collapse); training runtime and GPU memory; downstream 2D-CNN precision, recall, F1, accuracy on GAN-balanced vs imbalanced training sets [distribution; fidelity; utility-TSTR; efficiency]
- **Data:** MIT-BIH Arrhythmia (N, L, R, V, A beats grouped into normal/abnormal); leads: not reported; fs: 360 Hz; length: 10 (segments converted to 256x256 STFT spectrogram PNGs) s
- **Notes:** Explicit pitfall: pool_3 FID needs >2048 samples (else complex/NaN covariance); switching layer makes FID values non-comparable across works. Pairwise SSIM among synthetic samples used as mode-collapse/diversity detector.
- **Takeaway for ECGEN-Eval:** Add an intra-set pairwise-similarity diversity score (mode-collapse flag) and warn when sample count < embedding dim in Fréchet metrics.
- *Extraction source: full-text*
