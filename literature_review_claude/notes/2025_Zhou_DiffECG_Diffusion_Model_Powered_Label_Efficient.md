# DiffECG: Diffusion Model-Powered Label-Efficient and Personalized Arrhythmia Diagnosis
- **ID / Year / Venue:** P048 / 2025 / International Joint Conference on Artificial Intelligence
- **Model & task:** Diffusion (DDPM denoising U-Net used as self-supervised feature extractor; NAS-pruned encoder+bottleneck; multimodal feature fusion); other (diffusion-based self-supervised representation learning for arrhythmia detection; not a synthesis paper)
- **Losses:** standard DDPM noise-prediction loss for pre-training; classifier fine-tuning (cross-entropy); zeroth-order optimisation of noise step t using proposed gamma (loss-sensitivity) metric
- **Evaluation:** macro F1; macro accuracy (generalization cross-dataset and per-subject personalization) [utility-TSTR]
- **Data:** CPSC 2018; Chapman; PTB; Georgia; LTAF (long-term AF); leads: not reported; fs: not reported Hz; length: 6-60 s (CPSC), 10 s (Chapman, Georgia), 1-5 s (PTB), 24-48 h (LTAF) s
- **Notes:** No synthetic-ECG quality evaluation at all; diffusion denoiser used only as a feature extractor. Relevant mainly as evidence that diffusion U-Net features are discriminative (possible embedding backbone).
- **Takeaway for ECGEN-Eval:** Diffusion denoiser features could serve as an alternative embedding for FED-style metrics; otherwise little eval relevance.
- *Extraction source: full-text*
