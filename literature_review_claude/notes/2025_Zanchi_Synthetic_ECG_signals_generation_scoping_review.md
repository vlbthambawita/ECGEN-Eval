# Synthetic ECG signals generation: A scoping review
- **ID / Year / Venue:** P141 / 2025 / Computers in Biology and Medicine
- **Model & task:** Survey (79 studies to Jan 2024: mathematical modelling, computer-vision-inherited augmentation, deep generative models incl. VAEs, GAN variants, diffusion); survey
- **Losses:** not applicable
- **Evaluation:** catalogues visual inspection, classifier-performance gain, MSE-based (RMSE/PRD), MMD/KID, FD/FID, DTW variants, Pearson, Euclidean, MAE, SSIM, SNR, KL, EMD, t-SNE, ECG feature-distribution statistics (RR/QT/PR/QRS), Poincaré/DFA, discriminator-based measures, GAN-train/GAN-test, clinical Turing tests [fidelity, distribution, clinical, expert, utility-TSTR, diversity, privacy]
- **Data:** 79 reviewed studies; leads: various (single-lead dominant); fs: various Hz; length: various s
- **Notes:** Groups metrics into time-independent (distributional) and time-dependent (paired) families and shows they are implemented and paired inconsistently (all pairs, templates, real-vs-real or real-vs-noise baselines), making cross-study comparison impossible. Notes that independently generated leads break inter-lead dependencies and that DGMs cannot extend beyond training length. Main conclusion: the field needs standardized metrics that capture both fidelity and variability and are clinically meaningful.
- **Takeaway for ECGEN-Eval:** Directly supports ECGEN-Eval's purpose; the report should group metrics into distributional vs paired families, always show a real-vs-real (held-out) reference for every metric, and add clinical feature-distribution comparisons (RR, QT, PR, QRS) as first-class metrics.
- *Extraction source: full-text*
