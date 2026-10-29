# Morphology-preserving transfer-guided GAN with adaptive discriminative loss for robust and imbalanced ECG arrhythmia detection
- **ID / Year / Venue:** P106 / 2026 / Computers in Biology and Medicine
- **Model & task:** GAN (TG-MS-GAN: multi-stage coarse-to-fine pyramid with deformable convs, first stage initialised from a PTB-XL-pretrained generator) + EfficientNetV2-S classifier; minority-class augmentation for imbalanced arrhythmia classification
- **Losses:** hinge adversarial + discriminator feature-matching + cross-scale L1 consistency + discriminator agreement; classifier weighted CE + decayed center loss + focusing term
- **Evaluation:** paired Pearson, DTW, RMSE, PRD, cosine, SNR; overlays; accuracy, Macro-F1, AUPRC, confusion matrices; augmentation ablation vs SMOTE and single-scale GAN [fidelity, utility-TSTR]
- **Data:** MIT-BIH; Chapman-Shaoxing; PTB-XL; simulated Fetal ECG; leads: not reported; fs: not reported Hz; length: not reported (beats) s
- **Notes:** Morphology Pearson 0.987, PRD 2.13%, SNR 26.45 dB on unspecified real/generated pairs; Chapman augmentation gain acc 0.934->0.976, AUPRC 0.812->0.891. Fig. 1 says the augmented dataset is split into train/val/test, which (if true) puts synthetic samples in the test set; no distribution, diversity or memorisation checks.
- **Takeaway for ECGEN-Eval:** Near-perfect paired PRD/Pearson from a reconstruction-style GAN should trigger an nn_dist memorisation check; ECGEN-Eval reports should state how pairs were formed and warn when synthetic data could have entered a test split.
- *Extraction source: full-text*
