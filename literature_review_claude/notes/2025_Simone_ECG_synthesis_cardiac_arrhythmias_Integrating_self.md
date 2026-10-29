# ECG synthesis for cardiac arrhythmias: Integrating self-supervised learning and generative adversarial networks
- **ID / Year / Venue:** P061 / 2025 / Artificial Intelligence in Medicine
- **Model & task:** GAN (ECGAN: conditional WGAN with weight clipping; stacked-LSTM encoder/generator pre-trained by self-supervised L1 reconstruction, Conv1D discriminator); class-conditional binary rhythm synthesis (CHF, PVC, MI vs normal) for augmentation
- **Losses:** self-supervised L1 reconstruction (pre-training) + conditional Wasserstein adversarial loss with weight clipping
- **Evaluation:** FID and MMD on CNN-classifier activations; classifier-based Inception Score; Wasserstein distance; t-SNE; QT/QRS/PR/ST segment-duration boxplots via Pan-Tompkins delineation; augmentation accuracy/sensitivity/specificity/precision/F1; DTW (qualitative) [fidelity, distribution, diversity, clinical, utility-TSTR]
- **Data:** BIDMC CHF; MIT-BIH Arrhythmia (lead II); PTB Diagnostic (lead II); leads: 1; fs: 250 / 125 / 1000 Hz; length: single beats (BIDMC, MIT-BIH) and 1 s windows (PTB) s
- **Notes:** ECGAN best FID/IS/MMD on all datasets (BIDMC FID 233.9 vs TimeGAN 328.0, DDPM 743.3; PTB 8.60 vs 20.0) and +2.4% average augmentation accuracy with a leakage-free 20/70/10 SSL/generator/test split. FID/MMD use a task-specific classifier, so values are not comparable across datasets or papers; interval agreement shown only as boxplots.
- **Takeaway for ECGEN-Eval:** The clinical feature extractor should feed a quantitative real-vs-synthetic interval-distribution metric (e.g. per-interval JS/Wasserstein plus a delineation-failure rate), since this paper shows that baseline generators often fail delineation entirely, which is itself a useful validity signal.
- *Extraction source: full-text*
