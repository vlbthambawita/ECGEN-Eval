# Conditional Electrocardiogram Generation Using Hierarchical Variational Autoencoders

**Citation:** Ivan Sviridov and Konstantin Egorov. *Conditional Electrocardiogram Generation Using Hierarchical Variational Autoencoders*. arXiv, 2025. DOI: 10.3103/S0005105525701407. arXiv: 2503.13469v2; first public: 2025-03-03; peer-reviewed date: not verified.

**Source/version:** [paper.pdf](../papers/2025/Sviridov_2025_cNVAE/paper.pdf); [landing.html](../papers/2025/Sviridov_2025_cNVAE/landing.html). [Landing page](https://arxiv.org/abs/2503.13469v2).


**Task and model:** Conditional hierarchical Nouveau VAE adapted to 1D ECG; mixtures of logistic distributions and dependent channels; generate 8 leads then derive 12 (§III).

**Data and split:** PTB-XL 21,837; Georgia 10,344; Ningbo 34,905 records. 12 leads, 500 Hz, standardized to 10 s; per-lead 2.5–97.5 percentile filtering; random train/validation/test splits, explicit patient grouping unclear (§IV.B).

**Evaluation metrics:** Downstream per-class AUROC (%) averaged over training-data fractions; visual waveform/nearest-real comparisons; matched GPU training budget 134 h on A100. No distributional FID/MMD evaluation reported in own experiments (§§IV–V, TablesVI–VII, Figs2–6).

**Training objectives:** Hierarchical VAE training is described through NVAE architecture and mixture likelihood, but an explicit complete ECG objective and KL coefficients/schedule are not reported. TableV lists 5-epoch warmup and zero normalizing flows; this is not enough to infer KL annealing. Comparator WaveGAN/Pulse2Pulse GP weight=10 (TablesII–III).

**Reported evidence:** Ablates 1D versus 2D architecture and augmentation strategy, not ELBO components. MI-only augmentation gain up to 1.8 percentage points AUROC; both-class gain up to 1.5 (§V.A). Rare-class transfer sometimes worsens versus real-only pretraining (TablesVI–VII). CIs/seeds not reported.

**Clinical utility, experts and privacy:** Fixed real validation/test, synthetic proportions 0.1–1,1.5,2 for whole-data enrichment; 0.1–1 for minority enrichment; class-balanced synthetic pretraining and Georgia/Ningbo fine-tuning (§IV.A). No clinician or attack experiment; clinician validation is future work (§VI).

**Reproducibility:** https://github.com/univanxx/cNVAE_ECG (p.1), not inspected. Batch size 64 in prose versus 32 TableV; equations for limb leads contain a suspected typographical error. Preserve these discrepancies rather than silently correcting the paper.

**Critical assessment:** Reviewer assessment: useful external transfer design, but adaptation on external data is not zero-shot external validation; split ambiguity and absent loss specification limit attribution.
