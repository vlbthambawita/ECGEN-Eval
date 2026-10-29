# Progressive Two-Stage ECG Signal Generation: From Structural Skeletons to High-Fidelity Detail Refinement
- **ID / Year / Venue:** P164 / 2025 / IEEE International Conference on Bioinformatics and Biomedicine (BIBM)
- **Model & task:** Two-stage WGAN-GP: G1 maps noise to a square-wave P/QRS/T 'skeleton'; G2 refines it by attention-fusing features extracted from a real ECG; separate models per minority rhythm (AFIB, AT, AF) for augmentation
- **Losses:** WGAN-GP + decaying L1 structural consistency between G2 output and G1 skeleton
- **Evaluation:** intra-class distance; inter-class ED, MMD, KLD in an unspecified feature space; ResNet-18 augmented classification F1/recall/precision; ablation; qualitative plots [distribution, utility-TSTR, fidelity]
- **Data:** Resting ECG Segmentation Dataset (2,399 records, 12,730 2-s segments); leads: 1; fs: 500 Hz; length: 2 s
- **Notes:** AFIB ED 12.815, MMD 0.010, KLD 0.325; F1 0.672 vs 0.585 (no augmentation) and 0.632 (BI-DCGAN). The feature extractor is not named, MMD ties within 0.001 with no variance reported, and G2 takes real ECG as input when generating, so outputs are derived from specific real records and need a memorisation check. Category: a GAN, better filed under 01_GAN.
- **Takeaway for ECGEN-Eval:** The square-wave P/QRS/T encoding is a cheap structural representation; ECGEN-Eval could compare real vs synthetic wave-duration/amplitude distributions from its delineation module, and it should require that the embedding network for ED/MMD/KLD be named and that nn_dist be run when generators take real signals as input.
- *Extraction source: full-text*
