# Lightweight Multi-task CNN for ECG Diagnosis with GRU-Diffusion

**Citation:** Lehuai Xu and Zirui Lu and Haoran Yang and Yina Zhou. *Lightweight Multi-task CNN for ECG Diagnosis with GRU-Diffusion*. arXiv, 2025. DOI: not identified. arXiv: 2511.14104v1; first public: 2025-11-18; peer-reviewed date: not verified.

**Source/version:** [paper.pdf](../papers/2025/Xu_2025_DFNet/paper.pdf); [landing.html](../papers/2025/Xu_2025_DFNet/landing.html). [Landing page](https://arxiv.org/abs/2511.14104v1).


**Task and model:** GRU-Diffusion synthesizes minority ECG beats for augmentation; separate multitask classifier (pp.3–11).

**Data and split:** MIT-BIH two-lead and PTB 12-lead; selected single channel resampled250Hz,512 samples; shuffled80/20 record/sample split, no patient separation stated. Five minority MIT-BIH classes receive900 samples each.

**Evaluation metrics:** PCA feature FID, mean/SD DTW for random real–synthetic pairs, Welch PSD then KL; classification metrics assess augmentation. Metric extractor, normalization and pairing detail limited (pp.8–9).

**Training objectives:** Diffusion noise prediction follows DDPM; exact loss equation is standard DDPM MSE (Sec2.4), no extra ECG term. Separate DFNet classifier combines two cross-entropies and L2 regularization lambda=1e-5, task weights alpha/beta unspecified (p.7).

**Reported evidence:** Table2 average FID64.43→16.13; mean DTW133.28→111, KL.044→.0226. Some per-class DTW worsens (VFW 220.96→141.68 still improvement; compare all class values). Table5 augmentation gains classifier scores but shuffled split risks record leakage.

**Clinical utility, experts and privacy:** Augmentation benefit is tested; no real/fake panel, physiological biomarker, privacy attack or held-out patient design reported.

**Reproducibility:** PyTorch/RTR3090/Adam settings detailed; GAN/diffusion comparisons, loss schedule and exact feature model incomplete.

**Critical assessment:** FID+DTW+PSD cover distinct domains, but PCA FID and random-pair DTW are implementation-sensitive. Classification lift under non-patient split may overstate utility.
