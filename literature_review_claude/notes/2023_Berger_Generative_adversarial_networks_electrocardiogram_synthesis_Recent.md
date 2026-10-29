# Generative adversarial networks in electrocardiogram synthesis: Recent developments and challenges
- **ID / Year / Venue:** P171 / 2023 / Artificial Intelligence in Medicine
- **Model & task:** Survey/EvalOnly (PRISMA review of 30 GAN-for-ECG papers, 2019-2022: GAN, AC-GAN, C-GAN, DC-GAN, Sim-GAN, Pro-GAN, mixed); survey
- **Losses:** reviewed: minimax, Wasserstein, least squares, DTW-augmented, loss-sensitive GAN losses
- **Evaluation:** catalogues 20 quality metrics (distance: ED, RMSE, PRD, MAE, MSE, FD, FID, KID, KLD, MMD, DTW variants, TWED; correlation: NCC, Pearson, ADC; other: GAN-train/test, cosine similarity) plus classification gains [fidelity, distribution, utility-TSTR, expert]
- **Data:** 30 studies, mostly MIT-BIH-A single beats (23 studies), also PTB, PTB-XL, Chapman, CPSC2018 and private GESUS/Inter99; leads: various; fs: various Hz; length: various (mostly 0.35-1 s beats) s
- **Notes:** 9 studies quality-only, 11 classification-only, 10 both; augmentation gains ~6-7%. Point-wise distance/correlation metrics are criticised (Pearson ~1 everywhere, phase-shift sensitivity, reward copying); calls for physiological checks (RR distributions), reporting of augmentation amount and confusion matrices, and a gold-standard metric set.
- **Takeaway for ECGEN-Eval:** Directly motivates ECGEN-Eval: default to unpaired distributional metrics (mmd, fd/fed, swd, pr_dist) plus physiological checks (hrv, heart_rate, clinical features), and document that paired point-wise metrics (prd, mae, dtw, correlation) are only appropriate for translation/reconstruction tasks.
- *Extraction source: full-text*
