# CLEP-GAN: An Innovative Approach to Subject-Independent ECG Reconstruction from PPG Signals

**Citation:** Xiaoyan Li and Shixin Xu and Faisal Habib and Neda Aminnejad and Arvind Gupta and Huaxiong Huang. *CLEP-GAN: An Innovative Approach to Subject-Independent ECG Reconstruction from PPG Signals*. arXiv, 2025. DOI: not identified. arXiv: 2502.17536v1; first public: 2025-02-24; peer-reviewed date: not verified.

**Source/version:** [paper.pdf](../papers/2025/Li_2025_CLEPGAN/paper.pdf); [landing.html](../papers/2025/Li_2025_CLEPGAN/landing.html). [Landing page](https://arxiv.org/abs/2502.17536v1).


**Task and model:** CLEP-GAN and CLEP-VQGAN use contrastive PPG/ECG latent alignment and waveform GAN decoding for PPG-conditioned ECG synthesis (pp.15–18).

**Data and split:** BIDMC and CapnoBase paired PPG/ECG;34 pairs/dataset selected,15% random test split, subject-disjointness unclear.512 samples at125Hz (~4s).

**Evaluation metrics:** Paired RMSE, FD in feature space, HR MAE, RR interval mean/SD, RR-distribution rHI/rRMSE/rEMD/KL/KS; generator timing/FLOPs and FD efficiency table. Accuracy endpoints on generated traces are not diagnostic validation (pp.18–25).

**Training objectives:** Generation Eq.16: NT-Xent PPG→ECG tau.1 + smooth-L1 PPG autoencoding, ECG autoencoding, crossmodal ECG reconstruction. VQVAE variant adds dictionary/commitment losses lambda=.25 (Eqs.17–18). Time- and STFT-frequency logistic GAN losses, total alpha Lgen+beta Lt+gamma Lf; alpha30,beta3,gamma1 (Eqs.19–21).

**Reported evidence:** Table4: BIDMC RMSE .37 and FD22.27 CLEP-GAN; CapnoBase .33 and FD32.45. Ablation removing contrastive/adversarial losses has mixed HRV/error outcomes (Table7), so no uniform component win.

**Clinical utility, experts and privacy:** No clinician or privacy study. Synthesis uses paired translation, not independent random sampling. RR results include many nearly zero SD values suggesting errors in peak timing or reporting.

**Reproducibility:** Full arXiv v1 (52 pages), objective equations and code references; protocol has small selected test sets and epoch budgets differ among baselines.

**Critical assessment:** Useful stress test for frequency adversarial losses, but HRV and paired RMSE should be reported alongside clinically meaningful intervals; this is adjacent PPG translation.
