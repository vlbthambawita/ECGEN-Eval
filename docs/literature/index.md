# Literature Review: Evaluating Synthetic ECGs

This section summarises a systematic review of how **synthetic ECGs produced by
generative models** (GANs, VAEs, diffusion, flow matching, autoregressive/LLM models)
are **evaluated**, and which **loss functions** are used to train them.
It covers papers published or first posted between **October 2023 and October 2026**.

!!! tip "Explore the papers"
    The [Paper Database](database.md) lets you filter the reviewed papers by category, year,
    metric, metric type, loss function, task and dataset, query the underlying SQLite
    database with SQL, and export results as CSV.

## Scope and method

| Step | Count |
|---|---:|
| Unique records from arXiv, OpenAlex and Europe PMC (39 queries) | 2,957 |
| Kept after keyword/date pre-filter | 505 |
| Included after title/abstract screening | 153 |
| Added by snowballing (references and citations of 17 seed papers) and web search | 14 |
| **Included papers, Oct 2023 – Oct 2026** | **167** |
| Older background papers (2020 – Sep 2023) | 12 |
| Full text obtained (open access) — **currently in the database** | 91 |

Papers were included if they generate ECG signals with a machine-learning generative model
(including conditional tasks such as text-to-ECG, PPG-to-ECG and missing-lead reconstruction), or
propose or benchmark evaluation methods for synthetic ECGs. Per-paper data (model, task,
datasets, loss functions, evaluation metrics) was extracted from the full text.

!!! note "Database coverage"
    The database currently contains the 91 papers whose full text was available. The remaining
    papers were only seen as abstracts and will be added once their full text has been obtained.

## Evaluation categories

Each metric a paper uses is assigned one or two evaluation categories. The table counts papers
in the database (91 papers with full text) that evaluate each category. Click a category to
see its metrics and the papers that use them.

| Category | What it measures | Papers | Most used metric families (papers) |
|---|---|---:|---|
| [Fidelity](database.md#metrics/Fidelity) | Realism / similarity of synthetic samples to real data | 81 | RMSE (31); FID / embedding Fréchet (24); DTW (18); MAE (16) |
| [Diversity](database.md#metrics/Diversity) | Coverage and variety of the synthetic data (recall, mode collapse) | 20 | Precision / recall / density / coverage (7); t-SNE / UMAP / PCA plots (6); Inception-score-like (3); Diversity / mode-collapse measure (2) |
| [Utility](database.md#metrics/Utility) | Usefulness for downstream tasks (TSTR, TRTS, augmentation) | 66 | Augmentation gain (35); Downstream classification (21); TSTR / TRTS (16); Statistical tests (3) |
| [Privacy](database.md#metrics/Privacy) | Memorisation, re-identification and membership-inference risk | 9 | Membership inference / re-identification (7); Nearest-neighbour / DCR distance (3) |
| [Fairness](database.md#metrics/Fairness) | Behaviour across demographic subgroups; demographic attribute preservation | 8 | Subgroup performance gap (2); Demographic attribute preservation (2); Downstream classification (1); Augmentation gain (1) |
| [Robustness](database.md#metrics/Robustness) | Behaviour under noise, perturbation, domain shift; external validation | 50 | Cross-dataset / external validation (19); Seed / run variability (8); Metric sensitivity analysis (8); Noise / perturbation robustness (7) |
| [Clinical validity](database.md#metrics/Clinical%20validity) | Physiological plausibility: intervals, HR/HRV, fiducials, lead physics | 46 | Clinical intervals (PR/QRS/QT/ST) (17); Heart rate / HRV (13); Fiducial / R-peak timing (7); Inter-lead consistency (6) |
| [Human / expert](database.md#metrics/Human%20/%20expert) | Cardiologist ratings and visual Turing tests | 17 | Expert / Turing test (16); Expert diagnostic agreement (6); Statistical tests (1); Label / condition adherence (1) |
| [Conditional consistency](database.md#metrics/Conditional%20consistency) | Agreement between the generated ECG and the requested condition | 22 | Label / condition adherence (10); Text–ECG alignment (CLIP) (5); TSTR / TRTS (4); Expert diagnostic agreement (3) |
| [Efficiency](database.md#metrics/Efficiency) | Sampling cost: runtime, number of function evaluations, parameters | 17 | Efficiency (NFE / runtime / params) (15); Downstream classification (1) |

Fairness and privacy are rarely evaluated. Only a handful of papers compare quality or
utility across sex or age groups, or test for memorisation with membership-inference or
nearest-neighbour attacks. Robustness is mostly assessed by external or cross-dataset
validation, with fewer papers testing noise, seed variance or metric sensitivity.

## Most used evaluation metrics

Share of the 167 included papers whose evaluation uses each metric family (counted by keyword
matching of the extracted metric lists, so the numbers are approximate):

| Metric family | Papers | Type | In ECGEN-Eval |
|---|---:|---|---|
| Downstream classification (accuracy / F1 / AUROC) | 82 | utility | — |
| RMSE | 34 | fidelity | `mae` (RMSE in `extra`) |
| Pearson correlation | 33 | fidelity | — |
| MAE | 30 | fidelity | `mae` |
| Cardiologist assessment / visual Turing test | 25 | expert | — |
| Heart rate / HRV | 22 | clinical | `heart_rate`, `hrv` |
| MSE | 20 | fidelity | — |
| DTW | 18 | fidelity | `dtw` |
| TSTR / TRTS | 18 | utility | — |
| FID-style Fréchet distance on embeddings | 16 | distribution | `fed`, `fd` |
| PSNR / SNR | 16 | fidelity | `psnr` |
| Clinical intervals (PR / QRS / QT) | 16 | clinical | feature extraction only |
| Curve (discrete) Fréchet distance | 14 | fidelity | — |
| MMD | 12 | distribution | `mmd` |
| PRD | 12 | fidelity | `prd` |
| Manifold precision / recall / coverage | 10 | distribution | `pr_dist` |
| Privacy (membership inference, NN distance) | 9 | privacy | `nn_dist` (partial) |
| Inter-lead consistency (Einthoven, lead correlation) | 7 | clinical | — |
| Classifier two-sample test | 4 | distribution | — |

## Most used loss functions

| Loss / objective | Papers | Typical models |
|---|---:|---|
| Adversarial (minimax / BCE) | 50 | GAN, cGAN, pix2pix |
| L2 / MSE reconstruction | 39 | VAE, translation models |
| Diffusion noise prediction ($\lVert \epsilon - \epsilon_\theta(x_t, t, c) \rVert^2$) | 28 | DDPM, DDIM, SSSD, latent diffusion |
| KL divergence / ELBO | 22 | VAE, latent-diffusion autoencoders |
| Wasserstein + gradient penalty | 21 | GAN |
| Physiology / physics terms (ODE residual, Einthoven, R-peak or QRS masks) | 13 | GAN, diffusion, flow matching |
| Auxiliary classification cross-entropy | 13 | conditional GAN / diffusion |
| L1 reconstruction | 12 | cGAN translation |
| Spectral losses (FFT, STFT, Mel, wavelet critic) | 10 | GAN, diffusion |
| Flow-matching / rectified-flow velocity MSE | 7 | flow matching |

Recent papers typically keep the standard objective of their model family and add a
domain-specific term: a spectral loss, a physiological constraint, or a contrastive alignment
loss for text or PPG conditioning.

## Pitfalls reported in the literature

- **"FD" is ambiguous.** Some papers mean a curve Fréchet distance on raw signals, others an
  FID-style distance between Gaussians fitted to embeddings. FID values computed with different
  encoders are not comparable, and several papers do not name their encoder.
- **Good utility does not imply realism.** Classifiers trained on synthetic ECGs can perform well
  on real data while cardiologists still identify almost every synthetic ECG
  (low voltage, apparent electrode reversal, artefacts).
- **Weak distribution tests.** MMD and t-SNE/UMAP plots failed to separate real from synthetic
  data where a real-vs-synthetic classifier and TSTR/TRTS succeeded.
- **Point-wise errors mislead.** RMSE/MAE/PRD depend on sampling rate and flat segments,
  penalise small phase shifts, and can hide reduced amplitude variance.
- **No reference baseline.** Few papers report what the same metric gives for real-vs-real
  data; relative scores (e.g. FID(synthetic, real) / FID(real A, real B)) make results
  comparable.
- **Averages hide failures.** Per-lead errors can exceed 100 % on some leads while the
  average looks acceptable.
- **Leakage and selection bias.** Examples include selecting synthetic samples or checkpoints by
  downstream performance, using the test set for early stopping, or splitting one patient's
  segments across train and test.

## Implications for ECGEN-Eval

The review suggests these additions, in priority order:

1. Inter-lead consistency (Einthoven/Goldberger residuals, inter-lead correlation error).
2. Classifier two-sample test (real-vs-synthetic accuracy).
3. Train-on-synthetic / test-on-real (TSTR) and the reverse (TRTS).
4. Density and coverage, alongside the existing `pr_dist`.
5. Scores relative to a real-vs-real baseline.
6. Distribution distances on the clinical features ECGEN-Eval already extracts.
7. A physiological validity rate (failed R-peak detection, malformed QRS, implausible HR).
8. Metrics for paired tasks (Pearson r, shift-tolerant RMSE, fiducial timing error).
9. A fuller privacy suite (membership inference, distance to closest record).
10. Bootstrap confidence intervals and per-lead reporting by default.
