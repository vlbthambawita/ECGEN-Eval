# Conditional Electrocardiogram Generation Using Hierarchical Variational Autoencoders
- **ID / Year / Venue:** P038 / 2025 / arXiv
- **Model & task:** VAE (hierarchical conditional Nouveau VAE, cNVAE-ECG; also 2D-cNVAE-ECG variant); class-cond; augmentation
- **Losses:** NVAE ELBO: hierarchical KL terms + reconstruction likelihood modelled as mixture of discretized logistic distributions
- **Evaluation:** downstream AUROC of XResNet1d101 classifier: binary (MI vs SR) and multi-label (LAD, LVH, AF, STach, IAVB, SB, TAb) with varying synthetic proportions; transfer learning (pretrain on synthetic/real, fine-tune on Georgia/Ningbo)
- **Data:** PTB-XL (training, binary MI vs SR and multi-label); Georgia and Ningbo (PhysioNet/CinC 2021) for transfer-learning downstream evaluation; leads: 12; fs: 500; length: 10
- **Takeaway for ECGEN-Eval:** Augmentation-ratio sweeps and transfer-learning pretraining are useful utility protocols; complement with fidelity metrics.
- *Extraction source: full-text*
