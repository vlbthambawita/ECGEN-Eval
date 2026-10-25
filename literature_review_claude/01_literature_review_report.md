# Evaluation Methods and Loss Functions for Synthetic ECG Generation — Literature Review (Oct 2023 – Oct 2026)

- **Date:** 2026-10-25
- **Plan:** `00_review_plan.md` · **Search log:** `search_log.md` · **Screening:** `screening.csv` · **Per-paper data:** `papers_index.csv`, `notes/` · **Missing PDFs:** `to_download.md`
- Paper IDs (`P001`…`P179`) refer to rows in `papers_index.csv`; the full reference list is in §9.

---

## 1. Method summary (PRISMA-style flow)

```
Records identified (arXiv 15 queries, OpenAlex 15, Europe PMC 9)     n = 2,957 unique
  └─ excluded by keyword/date pre-filter (no ECG term, no generative
     term, or before 2023-10-01)                                     n = 2,452
Records screened on title + abstract                                 n =   505
  └─ excluded (classification-only, denoising, simulation, ECG
     images, deterministic reconstruction, other modality, …)        n =   352
Included from database search                                        n =   153
  + snowballing via OpenAlex refs/citations of 17 seed papers        n =    11
  + web-search gap filling (8 queries)                               n =     3
Included, in window (2023-10-01 → 2026-10-25)                        n =   167
  + background / seminal works (2020–2023-09, from snowballing)      n =    12
Total indexed                                                        n =   179
  ├─ full text obtained (open access; PDF validated)                 n =    91
  └─ abstract-only (paywalled or blocked; listed in to_download.md)  n =    88
```

The stopping criterion was met: the last round added 14 papers to the 153 already found (about 8%, below the 10% threshold).
Data were extracted by six parallel extraction passes. Each pass read the full text where available and the abstract otherwise, and every field records which source it came from.
Frequencies below were computed by **keyword-mapping the extracted metric and loss strings** onto metric and loss families. They are therefore approximate, and for abstract-only papers they are underestimates.

**Included papers by category (in-window, n = 167):** Diffusion 60 · GAN 54 · Hybrid/Other 16 · VAE 11 ·
Evaluation methods/benchmarks 11 · Flow matching/NF 7 · Surveys 6 · AR/Transformer/SSM/LLM 2.
**By year:** 2023 (Q4) 9 · 2024 36 · 2025 61 · 2026 61. The field is growing fast, and diffusion overtook GANs in 2025.

**Caveat:** P088 (graph-based ECG synthesis) turned out on full-text reading to be a biophysical Eikonal simulator, not a learned generative model. It is kept in the index and flagged, but its losses are not counted.

---

## 2. RQ1 — Which evaluation metrics are used, and how often?

Counts are the number of in-window papers (out of 167) whose extracted metric list matches each family.

| Rank | Metric family | # papers | Category |
|---:|---|---:|---|
| 1 | Downstream classification (Acc / F1 / AUROC; TSTR, TRTS, augmentation) | 82 | utility |
| 2 | RMSE | 34 | fidelity (paired / NN) |
| 3 | Pearson / correlation coefficient | 33 | fidelity |
| 4 | MAE | 30 | fidelity |
| 5 | Expert / cardiologist assessment, visual Turing test | 25 | expert |
| 6 | Heart rate / RR / HRV statistics | 22 | clinical |
| 7 | MSE | 20 | fidelity |
| 8 | Explicit TSTR / TRTS protocols | 18 | utility |
| 8 | DTW | 18 | fidelity |
| 8 | Statistical tests (KS, t-test, Mann-Whitney, Hotelling T², permutation) | 18 | distribution |
| 11 | FID-style Fréchet distance on learned embeddings (FID, FRD, FED, rFID, Context-FID) | 16 | distribution |
| 11 | PSNR / SNR | 16 | fidelity |
| 11 | Clinical intervals (PR, QRS, QT/QTc) | 16 | clinical |
| 14 | Discrete / curve Fréchet distance on raw signals (often just called "FD") | 14 | fidelity |
| 15 | MMD | 12 | distribution |
| 15 | KL / JS divergence (on PSDs, histograms, classifier outputs) | 12 | distribution |
| 15 | PRD | 12 | fidelity |
| 18 | Spectral / PSD similarity | 11 | fidelity |
| 18 | t-SNE / UMAP / PCA visual comparison | 11 | distribution (qualitative) |
| 20 | Manifold precision / recall / density / coverage (incl. related coverage/variance measures) | 10 | distribution |
| 21 | Privacy (membership inference, NN distance, NNAA, re-identification) | 9 | privacy |
| 21 | Wasserstein / EMD | 9 | distribution |
| 21 | SSIM | 9 | fidelity |
| 24 | Fiducial / R-peak timing error, R-peak detection F1 | 7 | clinical |
| 24 | Inter-lead consistency (Einthoven/Goldberger residual, inter-lead correlation-matrix error) | 7 | clinical / physics |
| 24 | Euclidean distance · cosine similarity | 7 · 7 | fidelity |
| 27 | Efficiency (NFE, sampling time) | 6 | efficiency |
| 28 | Classifier two-sample test / discriminative score / 1-NN accuracy | 4 | distribution |
| 28 | Text–ECG alignment (CLIP score) | 4 | conditional fidelity |
| 30 | TimeGAN predictive score · signal-quality index | 1 · 1 | utility · quality |

Category tags across papers (multi-label): utility 97 · fidelity 95 · distribution 59 · clinical 53 ·
efficiency 22 · expert 20 · privacy 11.

### Metric taxonomy and ECGEN-Eval coverage

| Metric | Category | One-line definition | # papers | Example papers | In ECGEN-Eval? |
|---|---|---|---:|---|---|
| RMSE / MSE / MAE | fidelity | Point-wise error, either paired (reconstruction/translation) or to the nearest neighbour (unconditional) | 34/20/30 | P004, P030, P072, P089, P114 | **partial** — `mae` (RMSE in `extra`) |
| PRD | fidelity | 100·‖x−x̂‖/‖x‖ | 12 | P037, P119, P165 | **yes** `prd` |
| Normalised PRD / NRMSE / NMAE | fidelity | Range-normalised versions that are less sensitive to flat segments and sampling rate | 2 | P119, P094 | no |
| Pearson correlation | fidelity | Linear correlation between paired/NN signals | 33 | P024, P066, P125, P127 | **no** |
| DTW | fidelity | Elastic alignment distance | 18 | P010, P094, P140, P167 | **yes** `dtw` |
| Discrete (curve) Fréchet distance | fidelity | Curve-matching distance on raw waveforms | 14 | P069, P125, P148, P165 | **no** (ECGEN `fd` is the *Gaussian* version) |
| PSNR / SNR | fidelity | Peak/mean signal-to-error ratio (dB) | 16 | P005, P089, P165 | **yes** `psnr` (SNR no) |
| SSIM | fidelity | 1-D structural similarity | 9 | P005, P089, P142 | **yes** `ssim` |
| Spectral similarity | fidelity | Distance between PSDs (JS/KL/Wasserstein/CMI) | 11 | P077, P100, P129 | **yes** `psd`, `spectral_entropy` |
| FID / FRD / FED on embeddings | distribution | Fréchet distance between Gaussians fitted to deep features | 16 | P049, P104, P123 (ECGFounder), P130, P178 | **yes** `fed` (+ `fd` on handcrafted features) |
| Relative FID (rFID) | distribution | FID(gen, real) / FID(real split A, real split B) | 3 | P130, P169, P094 (R-vs-R bands) | **no** |
| MMD (± permutation p-value) | distribution | Kernel two-sample statistic | 12 | P069, P120, P139 | **yes** `mmd` (no p-value) |
| Wasserstein / sliced Wasserstein / EMD | distribution | Optimal-transport distance | 9 | P023, P077, P119 | **yes** `swd` |
| Energy distance | distribution | Distance-based two-sample statistic | 1 | P069 | no |
| KL / JS on feature or HR distributions | distribution | Divergence between feature histograms | 12 | P034, P094, P100 | **partial** `hrv`, `heart_rate`, `spectral_entropy` |
| Precision / recall (k-NN manifold) | distribution | Fidelity vs coverage (Kynkäänniemi 2019) | 10 | P049, P067, P149, P178 | **yes** `pr_dist` |
| Density / coverage | distribution | Robust P/R variant (Naeem 2020) | 1 | P020 | **no** |
| Classifier two-sample test / discriminative score | distribution | Accuracy of a real-vs-synthetic classifier (0.5 = indistinguishable) | 4 | P034, P089, P102, P139 | **no** |
| Inception-score-like (ResNet Score) | distribution | Class-confidence × diversity from a classifier | 2 | P178 | no |
| Plausibility gap | distribution | KL between pretrained-classifier outputs on real vs synthetic | 1 | P036 | no |
| HR / HRV (SDNN, RMSSD, pNN50) | clinical | Rhythm statistics after R-peak detection | 22 | P007, P049 (HR-MAE vs condition), P074 | **yes** `heart_rate`, `hrv` |
| PR / QRS / QT / QTc / ST distributions | clinical | Delineated interval/amplitude statistics, often with Mann-Whitney / normal-range agreement | 16 | P094, P104, P113, P114, P066 | **features module only** (not a metric) |
| Fiducial / R-peak timing error, peak-detection F1 | clinical | Error in Q/R/S/T positions; detection failure rate | 7 | P004, P127, P151, P035, P076 | no |
| Validity rate (malformed QRS, flatline, failed delineation) | clinical | Share of samples failing hard physiological checks | 3 | P027, P076, P088 | no |
| Inter-lead consistency | clinical/physics | Einthoven (I+III=II), Goldberger residuals; inter-lead correlation-matrix error | 7 | P089, P107, P108, P130, P072 | **no** |
| Signal quality / per-sample quality score | quality | SQI, kurtosis, learned 4-level quality classifier | 3 | P131, P145, P066 | **partial** `sqi` |
| TSTR / TRTS / augmentation gain | utility | Classifier trained on synthetic, tested on real (and vice-versa) | 18 (+82 with downstream metrics) | P134, P139, P168, P126 | **no** |
| Label faithfulness / condition adherence | conditional | Pretrained classifier (or segmenter) agrees with the requested label/HR/text | 5 | P089, P049, P157, P133 | no |
| CLIP score (text–ECG) | conditional | Cosine similarity of text and ECG embeddings | 4 | P049, P067, P130, P149 | no |
| Membership inference / NNAA / DCR / re-identification | privacy | Distance-threshold attacks, nearest-neighbour adversarial accuracy, re-identification rate | 9 | P089, P113, P178, P179 | **partial** `nn_dist` (authenticity) |
| Expert Turing test (with specificity, κ) | expert | Cardiologists label real vs synthetic and/or diagnose | 25 | P049, P118, P134, P143, P168 | n/a (human) |
| Efficiency (NFE / wall-clock) | efficiency | Sampling cost vs quality curve | 6 | P077, P162, P101 | no |

---

## 3. RQ2 — Loss functions and training objectives by model family

Counts are the number of in-window papers whose extracted loss string matches each family.

| Loss / objective | Short form | # papers | Typical families | Example papers |
|---|---|---:|---|---|
| Adversarial (minimax / non-saturating BCE) | min_G max_D E[log D(x)] + E[log(1−D(G(z)))] | 50 | GAN, cGAN, pix2pix | P009, P110, P131, P142 |
| Wasserstein + gradient penalty (WGAN-GP) | E[D(G(z))] − E[D(x)] + λ‖∇D‖−1)², λ = 10 | 21 | GAN (most common stable choice) | P002, P026, P099, P103, P107 |
| Least-squares / hinge GAN | (D(x)−1)² + D(G(z))² | 3 | GAN, HiFi-GAN vocoders | P003, P174 |
| L2 / MSE reconstruction | ‖x−x̂‖² | 39 | VAE, translation, latent AEs | P042, P049 (VAE), P113, P123 |
| L1 reconstruction | ‖x−x̂‖₁ (pix2pix λ≈100) | 12 | cGAN translation, diffusion (L1 variant) | P030, P072, P177 |
| Diffusion ε-prediction MSE (DDPM L_simple) | ‖ε − ε_θ(x_t, t, c)‖² (+ L_vlb hybrid) | 28 | DDPM, DDIM, SSSD, latent diffusion | P056, P062, P134, P168, P049 |
| Flow matching / rectified-flow velocity MSE | ‖v_θ(x_t, t, c) − (x₁ − x₀)‖² (OT-CFM) | 7 | FM, rectified flow | P077, P112, P114, P118 |
| KL / ELBO | recon + β·KL(q(z\|x)‖p(z)); hierarchical KL (NVAE) | 22 | VAE, β-VAE, cVAE, latent-diffusion VAEs | P038, P042, P129, P151 |
| Auxiliary classification CE | ACGAN / class-consistency term | 13 | conditional GAN/diffusion | P103, P169, P001 |
| Spectral / frequency-domain loss | L1 on FFT amplitude, multi-resolution STFT/Mel, DWT critic | 10 | GAN, diffusion, VAE | P076 (FFT-L1), P089 (Mel), P002 (DWT critic), P034 (STFT discriminator), P130 |
| Physiology / physics constraints | ODE (McSharry) residual, Einthoven/Goldberger inter-lead, PDE residual, R-peak / QRS-mask losses, simulator-guided Euler | 13 | GAN, diffusion, FM | P107, P111, P130, P114, P004, P007, P065 |
| Contrastive / CLIP / InfoNCE | cross-modal alignment (PPG–ECG, text–ECG, same-patient) | 9 | FM, diffusion, hybrid | P015, P067, P114, P118 |
| VQ codebook + commitment | ‖sg[z_e]−e‖² + β‖z_e−sg[e]‖² | 7 | VQ-VAE, VQGAN, tokenisers | P015, P034, P178, P174 |
| Cycle-consistency | ‖F(G(x))−x‖₁ | 4 | CycleGAN | P003, P073, P135 |
| AR token cross-entropy | next-token NLL | 3 | Transformer / LLM | P149, P174 |
| MMD loss | MMD² to real latent bank | 2 | latent refinement | P120 |
| DTW loss | λ·DTW(real_i, fake_i) | 1 | cGAN | P010 (ABC-GAN) |
| Pearson-correlation loss | 1 − r | 1 | lead reconstruction | P066 |
| Perceptual / feature-matching | distance in pretrained ECG-encoder or discriminator feature space | 1–2 | VAE, HiFi-GAN | P123, P174 |
| Other | survival (Cox) loss P042; SI-SDR P053; quantile loss P013; kurtosis-based soft labels P131; Huber + cosine P013 | — | — | — |

**By family (in-window):**
- **GAN (54):** vanilla adversarial (40) > WGAN-GP (17). Each of L1/L2, auxiliary CE, physiology terms and spectral terms appears in about 5 papers.
- **Diffusion (60):** ε-prediction MSE dominates (25). Typical add-ons are a VAE reconstruction + KL term for latent diffusion (7), physiology constraints (5), spectral losses (4) and contrastive conditioning (3).
- **Flow matching (7):** velocity MSE (6), often plus cross-modal contrastive or VAE pre-training stages.
- **VAE (11):** ELBO (10), sometimes with perceptual or spectral terms.

**Trend:** most 2025–2026 papers keep the standard objective and add a **domain-specific auxiliary loss**:
- **Spectral:** Mel or STFT losses.
- **Physiological:** ODE or simulator residuals, Einthoven inter-lead terms, R-peak and QRS-mask losses.
- **Alignment:** CLIP-style contrastive terms.

The pure-adversarial objective is in decline.

---

## 4. RQ3 — Datasets and experimental setups

| Dataset | # in-window papers | Typical use |
|---|---:|---|
| MIT-BIH Arrhythmia | 39 | single-/two-lead beat generation, class balancing (360 Hz) |
| PTB-XL | 37 | 12-lead, 10 s, 100/500 Hz class-conditional generation; the de-facto benchmark (SSSD-ECG splits) |
| MIMIC-IV-ECG | 25 | large-scale 12-lead, text-report conditioning (DiffuSETS, SE-Diff, UniECG) |
| MIMIC-II/III waveforms, VitalDB, CapnoBase | 13 | PPG→ECG translation, ABP/ECG |
| BIDMC | 9 | PPG→ECG |
| WESAD / PPG-DaLiA | 8 | wearable PPG→ECG |
| PTB Diagnostic, Chapman-Shaoxing/Ningbo, CPSC, Georgia | 6–7 each | external validation, MI / rhythm classes |
| UK Biobank, CODE, CinC 2017, LTAF | 1 each | — |

**Setups:**
- Two dominant configurations:
  - **12-lead, 10 s at 100 Hz or 500 Hz** (PTB-XL / MIMIC-IV-ECG). Many diffusion papers generate 8 leads and derive the other 4 (SSSD-ECG convention).
  - **Single-lead heartbeats (~1 s) or short windows** from MIT-BIH.
- Long-duration generation is rare: minute-scale latent diffusion (P074) and 320 s windows. P074 found SDNN inflated in long synthetic recordings.
- Sampling rates and lengths are often not reported in abstracts, and many papers resample (e.g. DiffuSETS: 1024 samples per 10 s).

---

## 5. RQ4 — Is a standard emerging, and what pitfalls are reported?

**An emerging (but not yet standard) protocol.** In 2025–2026 the strongest papers converge on a *multi-level* evaluation:

1. **Signal or embedding distribution:** FID on a pretrained ECG encoder, plus manifold precision/recall or density/coverage.
   - Encoders seen: ECGFounder in P123; xResNet1d/ResNet in P104/P178; Net1D in P049; the model's own VAE in P130.
2. **Clinical features:** HR/HRV and PR/QRS/QT(c) distributions, adherence to the requested condition (e.g. HR-MAE, label faithfulness), and inter-lead consistency.
3. **Utility:** TSTR/TRTS or augmentation gain with a fixed classifier (xResNet1d50 since SSSD-ECG).
4. **Expert:** cardiologist Turing test and diagnostic agreement.
5. **(Increasingly) privacy:** membership-inference, NNAA and re-identification (P089, P113, P178, P179).

DiffuSETS (P049) explicitly proposes a three-level benchmark (signal, feature, diagnostic), and SE-Diff (P130) adopts it with *relative* FID and CLIP scores.
Two surveys (P141 scoping review; P171, 2023 GAN review: 20 different metrics across 30 GAN papers) and P012 conclude that **there is no standardised metric set**.

**Pitfalls reported in the literature (and found during extraction):**

1. **"FD" is ambiguous.** It denotes a discrete curve Fréchet distance on raw signals in at least 6 papers (P069, P125, P126, P148, P165, P041), and an FID-style Gaussian Fréchet distance in others (P110, P174, P178). Some papers mix the two (P079). FID values computed with different encoders (Inception pool_3 on spectrogram images in P142, ResNet, ECGFounder, a VAE) are not comparable, and several papers don't name the encoder at all (P047, P110).
2. **Good TSTR, but experts spot synthetic ECGs.** In SSSD-ECG-nle (P134), physicians identified 279/280 synthetic ECGs despite strong TSTR. The cues were low voltage, apparent chest-electrode reversal and artefacts. Utility metrics alone are insufficient.
3. **MMD and t-SNE/UMAP fail to separate real from synthetic** where classifier two-sample tests and TSTR/TRTS succeed (P139). P134 dropped DTW, MMD and Wasserstein as "uninformative".
4. **Metric robustness differs.** Stress-testing with controlled perturbations showed density/coverage were the most robust, while macro-AUROC barely changed until severe degradation (P020).
5. **Point-wise errors mislead.**
   - RMSE/MAE/PRD are diluted by flat segments and depend on sampling rate (P119).
   - They penalise phase shifts (P049 uses manifold P/R instead; P152 uses shift-tolerant min-RMSE).
   - Low RMSE in lead reconstruction hid regression to the mean: variance shrank (F-test p<0.05), and inter-lead R-amplitude correlation rose from R² 0.04 to 0.49 (P072).
6. **No reference baseline.** Distances are rarely put in context. Good practice is a real-vs-real reference:
   - rFID (P130, P169);
   - real intra- vs inter-subject bands (P094);
   - a "Real" row (P167, P178).
7. **Averaging hides failures.** Per-lead PRD exceeded 100% for limb leads III/aVF in every model while the mean looked acceptable (P037). Computing metrics only on class-mean beats hides diversity (P056, P080).
8. **Selection and leakage biases.**
   - Synthetic samples filtered by classifier gain or quality thresholds (P005, P041, P119).
   - GAN checkpoint chosen by downstream F1 (P103).
   - Test set used for early stopping (P016).
   - Same-patient segments split across train and test (P120; warned about in P085).
   - "100% accuracy" from training and testing on synthetic data only (P031).
9. **Small-sample estimates.** MMD/DTW on 16-sample batches (P062). FID with fewer samples than feature dimensions gives NaN/complex covariances (P142).
10. **Precision alone is misleading.** CGAN had precision 0.997 but recall 0.069 (P178). UniECG matched DiffuSETS precision with worse FID and recall (P149).
11. **Expert tests need specificity and κ.** In P143, raters were biased towards calling ECGs "real" (accuracy 40–42%, specificity 22–26%), and intra-rater κ ranged from −0.12 to 0.80.
12. **Spectral rankings depend on the PSD estimator.** Model rankings changed between FFT, DCT and Welch PSDs and between averaging schemes (P129).

---

## 6. RQ5 — Gap analysis against ECGEN-Eval

ECGEN-Eval already covers the signal-level and distribution-level core (`mmd, dtw, prd, psd, fd, fed, psnr, ssim, swd, mae, hrv, pr_dist, sqi, nn_dist, heart_rate, spectral_entropy`).
Its strongest differentiators relative to the literature are:
- `fed`, with three foundation-model backbones (encoder choice is the main comparability issue in the literature);
- `pr_dist`;
- the clinical feature extraction module.

The main gaps are in four areas:
- **utility metrics:** TSTR/TRTS;
- **classifier-based distribution tests:** C2ST;
- **clinical and physics consistency:** inter-lead consistency, clinical-interval distributions as metrics;
- **statistical hygiene:** reference baselines, confidence intervals, per-lead reporting.

---

## 7. Recommendations for ECGEN-Eval (ranked)

| # | Proposed metric / feature | Why (evidence) | Implementation notes |
|---|---|---|---|
| 1 | **`interlead`: inter-lead consistency** — Einthoven residual ‖I + III − II‖, Goldberger residuals (aVR + aVL + aVF ≈ 0), inter-lead correlation-matrix error ‖C_real − C_syn‖_F | Physics check missing from most metrics. Used as a metric (P089, P108) and as a loss (P107, P130). P134's lead-reversal artefacts would be caught | Requires `lead_names`. Residual only for 12-lead with limb leads; correlation-matrix error for any L ≥ 2. Lower is better |
| 2 | **`c2st`: classifier two-sample test** (real-vs-synthetic accuracy/AUROC; 0.5 ideal) | Detects differences MMD and t-SNE miss (P139); discriminative score (P102); 1-NN accuracy (P169) | Logistic regression / small 1D-CNN on handcrafted or `fed` embeddings, k-fold, report \|acc − 0.5\|. Optional 1-NN leave-one-out variant (no training) |
| 3 | **`tstr`: Train-on-Synthetic-Test-on-Real (+ TRTS)** | The most-reported utility protocol (18 explicit, 82 with downstream metrics). Standard since SSSD-ECG (P134, P139, P168) | Needs labels in `ECGDataset` metadata. Fixed lightweight classifier (e.g. sklearn on features or small xResNet1d). Report AUROC/F1 with TRTR as reference. Make optional (`[torch]`) |
| 4 | **`density_coverage`** (Naeem et al. 2020) | Most robust under perturbation (P020); complements `pr_dist` | Same k-NN machinery as `pr_dist`; add as `extra` fields or a separate key |
| 5 | **Real-vs-real reference / relative scores** (e.g. rFID = FID(syn, real) / FID(real_A, real_B)) | Makes scores interpretable across datasets and encoders (P130, P169, P094, P178) | Generic wrapper: split real data in half, compute the metric on real-vs-real, report `score`, `ref_score`, `ratio`. Show it in the HTML report |
| 6 | **`clinical_dist`: clinical-feature distribution distances** — per-feature Wasserstein/KS/JS on PR, QRS, QT, QTc, ST, T-amp; normal-range agreement | 16 papers evaluate interval distributions (P094, P104, P113, P114). ECGEN-Eval already extracts these features but has no scalar metric | Reuse `FeatureExtractor` `summary_df`. Per-feature distance in `per_lead`/`extra`. Also report KS p-values and the share of values within clinical normal ranges |
| 7 | **`validity`: physiological validity rate** — R-peak detection failure, missing/malformed QRS, flat-line, implausible HR (<30 or >220 bpm) | 30% malformed QRS in P027; peak-detection failures in P076; hard filters in P088 | Cheap per-sample checks from `qrs_detection`; higher is better |
| 8 | **Paired-task metrics** (when `--paired`): Pearson r, shift-tolerant min-RMSE (P152), fiducial / R-peak timing error (P004, P127, P151), R-peak F1 (P035), SI-SDR (P053) | Translation / reconstruction (PPG→ECG, lead reconstruction) is ~25% of the literature, and correlation is the 3rd most-used metric | Add a `paired=True` mode to `BaseMetric` or a `paired` metrics group. Pearson can also go into `mae.extra` for NN pairs |
| 9 | **Privacy suite**: DCR distribution (synthetic→train vs holdout→train), distance-threshold membership-inference F1, NNAA | Increasingly expected (P089, P113, P178, P179); `nn_dist` covers only part | Requires a held-out real split. Extend `nn_dist.extra` with MIA-F1 over thresholds and NNAA |
| 10 | **`condition_adherence`**: label faithfulness via a pretrained classifier; HR-MAE vs the requested HR; CLIP score for text-conditioned models | Conditional generators dominate 2025–26 (P049, P089, P130, P149) | Pluggable classifier/encoder (reuse `encoders/`). Only active when conditions are supplied |
| 11 | **Statistical hygiene in the report**: bootstrap 95% CIs for every scalar, MMD/energy permutation p-values (P069), per-lead tables by default (P037), sample-size warnings (P062, P142) | Pitfalls 6–9 above | Generic bootstrap wrapper over `compute()`. Warn when N < feature dimension for Fréchet metrics |
| 12 | **Disambiguate "FD"**: document that `fd` is the Gaussian Fréchet distance. Optionally add `curve_fd` (discrete Fréchet on raw waveforms) for comparability with the 14 papers that use it | Pitfall 1 | Docs change plus a small O(n·m) dynamic-programming implementation |
| 13 | Optional: **energy distance**, **SNR**, **NRMSE/NPRD** (range-normalised) | Used in P069, P089, P119 | Small additions to existing metrics |
| 14 | Optional: **efficiency reporting** (NFE / samples per second) as report metadata | P077, P162 | Report field, not a metric |

---

## 8. The five most important papers for this project

1. **P049 — DiffuSETS (2025).** Text-conditioned 12-lead latent diffusion on MIMIC-IV-ECG. It proposes the three-level evaluation benchmark (signal: FID + manifold P/R; feature: HR-MAE; diagnostic: CLIP score), plus a cardiologist Turing test. This is the reference protocol later papers adopt (P130, P149).
2. **P020 — Assessing the robustness of evaluation metrics for synthetic ECG signal quality (2026).** It stress-tests fidelity, diversity, privacy and utility metrics with controlled perturbations on five generators. Density/coverage are the most robust. This is direct guidance for metric selection in ECGEN-Eval (abstract only so far; high priority in `to_download.md`).
3. **P134 — SSSD-ECG-nle (2024), together with the background SSSD-ECG paper P168.** These set the PTB-XL / TSTR / xResNet1d50 benchmark convention, and show that strong TSTR coexists with near-perfect expert detection of synthetic ECGs.
4. **P094 — Comprehensive Framework for Synthetic ECG Validation (2026).** A four-layer validation (visual, NeuroKit morphology with statistical tests, similarity metrics against real-vs-real intra- and inter-subject bands, expert scoring), with patient-level statistics.
5. **P129 — Shape and amplitude decoupling in pulsatile signal synthesis and its evaluation (Nature Communications, 2026).** It introduces conditional-mutual-information spectral metrics and a composite ISCORE, and shows that rankings depend on the PSD estimator and aggregation choice. This is important for ECGEN-Eval's `psd` metric.

Also important:
- **P130 (SE-Diff):** relative FID and CLIP scores, plus Einthoven/ODE losses.
- **P089 (MIDT-ECG):** inter-lead correlation error, NNAA/MIA privacy, Mel-spectrogram loss.
- **P139:** C2ST beats MMD and t-SNE.
- **P178:** FRD, ResNet Score, MIA.
- **P077 (FlowECG):** flow matching versus diffusion at a given NFE.
- **P012:** a key-metrics review that proposes a standard framework (abstract only so far).

---

## 9. References

Full bibliographic data (authors, venue, DOI/URL, PDF path, extracted losses and metrics) for all 179 papers is in
`papers_index.csv`. Per-paper summaries are in `notes/`. The compact list below was generated from the index.

- **P001** Nguyen Van Nam, Tran Thi Hoa, Le Minh Duc (2025). A Diffusion-Based Generative Framework for Synthetic Arrhythmia ECG Signals. *Journal of Artificial Intelligence for Healthcare Systems*. https://doi.org/10.68159/a740774739
- **P002** Rashmi Kumari, Prateek Agrawal, Spandan More et al. (2024). A Generative Methodology for PPG to ECG Reconstruction Based on Dual-Critic Approach. *Computing in cardiology*. https://doi.org/10.22489/cinc.2024.486
- **P003** Swarajya Madhuri Rayavarapu, Tammineni Shanmukha Prasanthi, Gottapu Santosh Kumar et al. (2023). A GENERATIVE MODEL FOR DEEP FAKE AUGMENTATION OF PHONOCARDIOGRAM AND ELECTROCARDIOGRAM SIGNALS USING LSGAN AND CYCLE GAN. *Informatyka Automatyka Pomiary w Gospodarce i Ochronie Środowiska*. https://doi.org/10.35784/iapgos.3783
- **P004** Cho HM, Han S, Seong JK et al. (2026). A peak-oriented diffusion model for high-fidelity electrocardiogram reconstruction from photoplethysmogram: development and usability study. *BioData mining*. https://doi.org/10.1186/s13040-026-00544-2
- **P005** Jiaqi Liu, Kwok Tai Chui, Lap–Kei Lee et al. (2025). A performance analysis of convolutional autoencoder modified WaveGAN architectures for realistic 12 lead electrocardiogram synthesis. *Scientific Reports*. https://doi.org/10.1038/s41598-025-20470-3
- **P006** Mingzhe Liu, Hongpo Zhang (2025). A Personalized ECG Lead Reconstruction Method Based on Denoising Diffusion Model. *n/a*. https://doi.org/10.1145/3730436.3730464 — *not downloaded*
- **P007** Xi Qiu, Hailin Cao, L. Q. Yang et al. (2026). A Physics-Aware Diffusion Framework for Robust ECG Synthesis Using Mesoscopic Lattice Boltzmann Constraints. *Biology*. https://doi.org/10.3390/biology15050431
- **P008** Min-Gu Kim, Jaehyo Jung (2026). A U-Net Based LSGAN Framework for 12-Lead ECG Synthesis in Wearable IoMT Systems. *IEEE Internet of Things Journal*. https://doi.org/10.1109/jiot.2026.3686449 — *not downloaded*
- **P009** Francesco Speziale, Ugo Lomoio, Fabiola Boccuto et al. (2026). A Usable GAN-Based Tool for Synthetic ECG Generation in Cardiac Amyloidosis Research. *arXiv*. https://doi.org/10.48550/arxiv.2601.08260
- **P010** Parmida Behain, Noushin Riahi (2026). ABC-GAN: An Attention-Based Conditional GAN with DTW Loss for ECG Signal Generation to Address Class Imbalance. *Journal of Information Systems and Telecommunication (JIST)*. https://doi.org/10.66224/jist.51397.14.54.79
- **P011** Georgios Kritopoulos, Georgios Neofotistos, Georgios D. Barmparis et al. (2026). Addressing Class Imbalance in ECG Arrhythmia Classification Using Latent Diffusion and Quantum-Enhanced Generative Modeling. *AI in Medicine*. https://doi.org/10.3390/aimed1030023 — *not downloaded*
- **P012** Wei Wang, Jing Ma, Kuanquan Wang et al. (2025). Advancing electrocardiogram synthesis: Analyzing key metrics for enhanced evaluation. *Computers in Biology and Medicine*. https://doi.org/10.1016/j.compbiomed.2025.110879 — *not downloaded*
- **P013** Khan MR, Haider ZM, Hussain J et al. (2026). AI based ECG data recovery and cardiovascular diseases classification (CEDRC-network). *Scientific reports*. https://doi.org/10.1038/s41598-026-46232-3
- **P014** Simon Eggleton, B. Gallego, J. Ryan (2026). AI Generated Synthetic Electrocardiograms Demonstrate Morphological Preservation. *Heart Lung and Circulation*. https://doi.org/10.1016/j.hlc.2026.07.593 — *not downloaded*
- **P015** Zhengyao Ding, Yujian Hu, Ziyu Li et al. (2025). AI modeling photoplethysmography to electrocardiography useful for predicting cardiovascular disease. *npj Digital Medicine*. https://doi.org/10.1038/s41746-025-02228-3
- **P016** Aditya Mallick, Rahul L R, Albert Shaiju et al. (2024). AI-based 3-Lead to 12-Lead ECG Reconstruction: Towards Smartphone-based Public Healthcare. *arXiv*. https://doi.org/10.1109/healthcom60970.2024.10880752
- **P017** Thi Diem Tran, Thi Thu Khiet Dang, Ngoc Quoc Tran (2024). An Innovative Approach for Long ECG Synthesis with Wasserstein GAN Model. *Lecture notes in computer science*. https://doi.org/10.1007/978-3-031-64608-9_22 — *not downloaded*
- **P018** José Fernando Núñez, Jamie Arjona, Adrián Tormos et al. (2023). Applying Generative Models and Transfer Learning to Physiological Data Classification. *Frontiers in artificial intelligence and applications*. https://doi.org/10.3233/faia230656 — *not downloaded*
- **P019** H. Kamalanathan, A Vuong, Stephen Bacchi et al. (2026). Are AI-generated electrocardiograms clinically accurate? Benchmarking accuracy of AI-generated ECGs: a multiplatform performance study of public LLMs. *European Heart Journal - Digital Health*. https://doi.org/10.1093/ehjdh/ztaf143.121
- **P020** Maria Russo, Inês Sousa, Ricardo Santos et al. (2026). Assessing the robustness of evaluation metrics for synthetic ECG signal quality. *Computers in Biology and Medicine*. https://doi.org/10.1016/j.compbiomed.2026.111824 — *not downloaded*
- **P021** Ali Nawaz, Mubarak Albarka Umar, Khaled Shuaib et al. (2024). Autoencoder-based Arrhythmia Detection using Synthetic ECG Generation Technique. *Annual International Conference of the IEEE Engineering in Medicine and Biology Society. IEEE Engineering in Medicine and Biology Society. Annual International Conference*. https://doi.org/10.1109/embc53108.2024.10781537 — *not downloaded*
- **P022** Bedin, Lisa (2025). Avancées dans les Modèles Génératifs : Méthodologies et Applications à la Cardiologie. *HAL*. https://doi.org/10.70675/58f8ffe6z5eb0z4b5fza7fez4aa8c78eed69 — *not downloaded*
- **P023** Gabriel V. Cardoso, Lisa Bedin, Josselin Duchateau et al. (2023). Bayesian ECG reconstruction using denoising diffusion generative models. *arXiv*. https://doi.org/10.48550/arxiv.2401.05388
- **P024** Xiaoyan Li, Shixin Xu, Faisal Habib et al. (2025). Beyond Single-Channel: Multichannel Signal Imaging for PPG-to-ECG Reconstruction with Vision Transformers. *arXiv*. https://arxiv.org/abs/2505.21767
- **P025** Lorenzo Simone (2026). Beyond Synthetic Data: Generative Deep Learning from ECG Modeling and Anomaly Detection to Machine Unlearning. *Electronic Theses and Dissertations Repository (University of Pisa)*.  — *not downloaded*
- **P026** Archana Venugopal, Diego R. Faria (2024). Boosting EEG and ECG Classification with Synthetic Biophysical Data Generated via Generative Adversarial Networks. *Applied Sciences*. https://doi.org/10.3390/app142310818
- **P027** Kranz Dominik, Oruç Kahriman, Niels Wessel et al. (2024). Can Diffusion Models Understand the Long Term Dependencies in an ECG?. *n/a*. https://doi.org/10.47952/gro-publ-214 — *not downloaded*
- **P028** Yuta Nambu, Masahiro Kohjima, Ryûji Yamamoto (2025). CardioFlow: Learning to Generate ECG from PPG with Rectified Flow. *IEEE International Conference on Acoustics Speech and Signal Processing*. https://doi.org/10.1109/icassp49660.2025.10888856 — *not downloaded*
- **P029** Rongjia Wang, Xunde Dong, Xiuling Liu et al. (2026). CDM-DL-PSI: A conditional diffusion model for 12-Lead ECG generation using disease labels and patient-specific information. *Biomedical Signal Processing and Control*. https://doi.org/10.1016/j.bspc.2026.109927 — *not downloaded*
- **P030** Gi-Won Yoon, Segyeong Joo (2024). Classification feasibility test on multi-lead electrocardiography signals generated from single-lead electrocardiography signals. *Scientific Reports*. https://doi.org/10.1038/s41598-024-52216-y
- **P031** Turgut Özseven (2024). Classification of ECG Signals Using GAN, SMOTE, and VAE Data Augmentation Methods: Synthetic vs. Real. *Bitlis Eren Üniversitesi Fen Bilimleri Dergisi*. https://doi.org/10.17798/bitlisfen.1523524
- **P032** Jinhee Kwak, Jaehee Jung (2024). Classification of imbalanced ECGs through segmentation models and augmented by conditional diffusion model. *PeerJ Computer Science*. https://doi.org/10.7717/peerj-cs.2299
- **P033** Hongtao Chen, Shota Kato, Kana Eguchi et al. (2025). Classifier-Guided Diffusion Model for Generating Disease-Specific ECG Data: A Case Pilot Study on Inferior Myocardial Infarction. *Annual International Conference of the IEEE Engineering in Medicine and Biology Society. IEEE Engineering in Medicine and Biology Society. Annual International Conference*. https://doi.org/10.1109/embc58623.2025.11253197 — *not downloaded*
- **P034** Xiaoyan Li, Shixin Xu, Faisal Habib et al. (2025). CLEP-GAN: An Innovative Approach to Subject-Independent ECG Reconstruction from PPG Signals. *arXiv*. https://doi.org/10.1186/s12859-025-06276-0
- **P035** Bo Cui, Xiaowen Song, Yaowen Zhang et al. (2026). Compact Latent Manifold Translation: A Parameter-Efficient Foundation Model for Cross-Modal and Cross-Frequency Physiological Signal Synthesis. *arXiv*. https://doi.org/10.48550/arxiv.2605.13248
- **P036** Timothy Oladunni, Farouk Ganiyu-Adewumi, Clyde Baidoo et al. (2026). Complementarity-Preserving Generative Theory for Multimodal ECG Synthesis: A Quantum-Inspired Approach. *arXiv*. https://doi.org/10.48550/arxiv.2603.26695
- **P037** Xiaoyang Wei, Zhiyuan Li, Yuanyuan Tian et al. (2026). Condition-fusion-and-hiding denoising diffusion model for electrocardiogram lead reconstruction. *iScience*. https://doi.org/10.1016/j.isci.2026.115188
- **P038** Ivan Sviridov, Konstantin Egorov (2025). Conditional Electrocardiogram Generation Using Hierarchical Variational Autoencoders. *arXiv*. https://doi.org/10.3103/S0005105525701407
- **P039** Zehui Zhan, Jia‐Rong Chen, Kangming Li et al. (2024). Conditional generative adversarial network driven variable-duration single-lead to 12-lead electrocardiogram reconstruction. *Biomedical Signal Processing and Control*. https://doi.org/10.1016/j.bspc.2024.106377 — *not downloaded*
- **P040** Ahmed Tibermacine, Imad Eddine Tibermacine, M’hamed Mancer et al. (2026). Cross-Lead Attention Transformers with GAN Oversampling for Robust ECG Arrhythmia Detection. *Electronics*. https://doi.org/10.3390/electronics15061258 — *not downloaded*
- **P041** Yang Y, Lan T, Wang Y et al. (2024). Data imbalance in cardiac health diagnostics using CECG-GAN. *Scientific reports*. https://doi.org/10.1038/s41598-024-65619-8
- **P042** Sang Y, Banerjee A, Beetz M et al. (2025). Deep conditional generative model for personalization of 12-lead electrocardiograms and cardiovascular risk prediction. *Frontiers in digital health*. https://doi.org/10.3389/fdgth.2025.1558589
- **P043** Giuliana Monachino, Beatrice Zanchi, Luigi Fiorillo et al. (2023). Deep Generative Models: The winning key for large and easily accessible ECG datasets?. *Computers in Biology and Medicine*. https://doi.org/10.1016/j.compbiomed.2023.107655 — *not downloaded*
- **P044** Yuchen Wang, Y.F. Li, Yongjian Li et al. (2025). Deep Learning Driven Physiological Signal Generation: An Improved DDIM-Based ECG Synthesis Framework. *International Congress on Image and Signal Processing, BioMedical Engineering and Informatics (CISP-BMEI)*. https://doi.org/10.1109/cisp-bmei68103.2025.11259385 — *not downloaded*
- **P045** Julius Vetter (2026). Deep Probabilistic Models for Physiological Time Series: Prediction, Generation, and Inference. *n/a*. https://doi.org/10.15496/publikation-115681 — *not downloaded*
- **P046** Rongjia Wang, Yihai Fang, Jianhong Dou et al. (2026). Diff-TGEG: a novel diffusion model for text-guided electrocardiogram generation. *International Conference on Algorithms, High Performance Computing and Artificial Intelligence (AHPCAI)*. https://doi.org/10.1117/12.3107452 — *not downloaded*
- **P047** Nour Neifar, Achraf Ben Hamadou, Afef Mdhaffar et al. (2024). DiffECG: A Versatile Probabilistic Diffusion Model for ECG Signals Synthesis. *IEEE/ACIS International Conference on Software Engineering Research, Management and Applications (SERA)*. https://doi.org/10.1109/sera61261.2024.10685651
- **P048** Tianren Zhou, Zhenge Jia, Dongxiao Yu et al. (2025). DiffECG: Diffusion Model-Powered Label-Efficient and Personalized Arrhythmia Diagnosis. *International Joint Conference on Artificial Intelligence*. https://doi.org/10.24963/ijcai.2025/890
- **P049** Yongfan Lai, Jiabo Chen, Deyun Zhang et al. (2025). DiffuSETS: 12-lead ECG Generation Conditioned on Clinical Text Reports and Patient-Specific Information. *arXiv*. https://doi.org/10.1016/j.patter.2025.101291
- **P050** Yuan Wang, Yu Weng, Wengjian Liu (2025). Diffusion Model-Based Multi-scale Feature and Timing Consistency Enhancement for ECG Signal Generation. *Lecture notes in computer science*. https://doi.org/10.1007/978-981-95-3001-4_30 — *not downloaded*
- **P051** Rong Xiao, Zhijun Xiao, Jianqing Li et al. (2026). Disentangled conditional generation of ECG signals with interpretable latent factors. *Computer Methods and Programs in Biomedicine*. https://doi.org/10.1016/j.cmpb.2026.109621 — *not downloaded*
- **P052** Chenyang Xu, Siming Li, Wensai Xuan et al. (2026). Disentangling Physiology from Fidelity: Latent-Guided Diffusion Models for Cross-Modal Cardiac Synthesis. *IEEE International Conference on Acoustics Speech and Signal Processing*. https://doi.org/10.1109/icassp55912.2026.11464795 — *not downloaded*
- **P053** Fan-Yi Hsu, I Chiu, Kuan-Chen Wang et al. (2026). DiSR-ECG: Residual Shifting Conditional Diffusion for Robust ECG Super-Resolution. *arXiv*. https://doi.org/10.48550/arxiv.2609.16619
- **P054** Tiantian Du, Jiwei Wang, Rui Qu et al. (2024). DS4U-Net: A Diffusion Model-Based Approach to Multi-Lead ECG Signal Generation. *International Conference on Intelligent Computing and Signal Processing (ICSP)*. https://doi.org/10.1109/icsp62122.2024.10743556 — *not downloaded*
- **P055** Feiyan Zhou, Jiajia Li (2024). ECG data enhancement method using generate adversarial networks based on Bi-LSTM and CBAM. *Physiological Measurement*. https://doi.org/10.1088/1361-6579/ad2218 — *not downloaded*
- **P056** Zhongyu Wang, Caiyun Ma, Minghui Zhao et al. (2024). ECG Generation Based on Denoising Diffusion Probabilistic Models. *Computing in cardiology*. https://doi.org/10.22489/cinc.2024.027
- **P057** Oumaima Chehaibi, Nesrine Majdoub, Taoufik Ladhari et al. (2024). ECG Monitor Design: From One to Three - Advancing ECG Monitoring with AI-Generated Lead Synthesis (GANs). *n/a*. https://doi.org/10.1109/icaige62696.2024.10776701 — *not downloaded*
- **P058** Hanbin Xiao, Yong Xia (2025). ECG signal generation using feature disentanglement auto-encoder. *Physiological Measurement*. https://doi.org/10.1088/1361-6579/adab4f — *not downloaded*
- **P059** Rong Xiao, Shuo Zhang, Zhongyu Wang et al. (2025). ECG Signal Generation Using Variable β-Conditional Variational Autoencoder. *Annual International Conference of the IEEE Engineering in Medicine and Biology Society. IEEE Engineering in Medicine and Biology Society. Annual International Conference*. https://doi.org/10.1109/embc58623.2025.11251611 — *not downloaded*
- **P060** Sanketa Hegde, Merten Prüser, Nikola Cenic et al. (2025). ECG Synthesis and Utility Analysis - A Diffusion Model Based Approach. *Studies in health technology and informatics*. https://doi.org/10.3233/shti251414 — *not downloaded*
- **P061** Lorenzo Simone, Davide Bacciu, Vincenzo Gervasi (2025). ECG synthesis for cardiac arrhythmias: Integrating self-supervised learning and generative adversarial networks. *Artificial Intelligence in Medicine*. https://doi.org/10.1016/j.artmed.2025.103162 — *not downloaded*
- **P062** Md Haider Zama, Friedhelm Schwenker (2023). ECG Synthesis via Diffusion-Based State Space Augmented Transformer. *Sensors*. https://doi.org/10.3390/s23198328
- **P063** Leya Li, Tong Xia, Haojie Zhang et al. (2024). ECG-DPM: Electrocardiogram Generation via a Spectrogram-based Diffusion Probabilistic Model. *IEEE Smart World Congress (SWC)*. https://doi.org/10.1109/swc62898.2024.00074 — *not downloaded*
- **P064** Deng Jie, Xu Tianbo, Xu Hongzheng (2026). ECG-QRFGAN: A Quantum Residual Forest Generative Adversarial Network for Electrocardiogram Synthesis. *International Conference on Biomedicine and Bioinformatics Engineering (ICBBE)*. https://doi.org/10.1145/3822183.3822248 — *not downloaded*
- **P065** Zhikang Chen, Yue Wang, Sen Cui et al. (2026). ECG-WM: A Physiology-Informed ECG World Model for Clinical Intervention Simulation. *arXiv*. https://doi.org/10.48550/arxiv.2605.17580
- **P066** Alex Lence, Federica Granese, Ahmad Fall et al. (2024). ECGrecover: a Deep Learning Approach for Electrocardiogram Signal Completion. *arXiv*. https://doi.org/10.1145/3690624.3709405
- **P067** Yongfan Lai, Bo Liu, Xinyan Guan et al. (2025). ECGTwin: Personalized ECG Generation Using Controllable Diffusion Model. *arXiv*. https://arxiv.org/abs/2508.02720
- **P068** Victor Ramon França Bezerra de Souza, Lucas Bernardino Cardoso, Ângelo Perkusich et al. (2026). Electrocardiogram Synthesis from Photoplethysmogram Signals Through Generative Adversarial Networks. *IEEE Latin American Symposium on Circuits and Systems (LASCAS)*. https://doi.org/10.1109/lascas67804.2026.11457124 — *not downloaded*
- **P069** Murat Yalcin, Marc Erich Latoschik (2026). End-to-end non-invasive ECG signal generation from PPG signal: a self-supervised learning approach. *Frontiers in Physiology*. https://doi.org/10.3389/fphys.2026.1694995
- **P070** Oscal Tzyh-Chiang Chen, Yue-Han Li, Chu Wang et al. (2025). Enhancing cardiac disease recognition with generative model-based data augmentation. *IET conference proceedings.*. https://doi.org/10.1049/icp.2025.2584 — *not downloaded*
- **P071** Yongchao Wang, Guo F, Shizhan Tang et al. (2026). Enhancing Inter-Lead Correlations: A Novel Diffusion GAN Framework for 12-Lead ECG Generation. *IEEE International Conference on Acoustics Speech and Signal Processing*. https://doi.org/10.1109/icassp55912.2026.11463110 — *not downloaded*
- **P072** Oriana Presacan, Alexandru Dorobanțiu, Jonas Lynggaard Isaksen et al. (2025). Evaluating the feasibility of 12-lead electrocardiogram reconstruction from limited leads using deep learning. *Communications Medicine*. https://doi.org/10.1038/s43856-025-00814-w
- **P073** Sara Battiston, Roberto Sassi, Massimo Walter Rivolta (2024). Evaluating the Quality of CycleGAN Generated ECG Data for Myocardial Infarction Classification. *Computing in cardiology*. https://doi.org/10.22489/cinc.2024.457
- **P074** Dominik D. Kranz, Jan F. Kraemer, Oruç Kahriman et al. (2025). Exploring latent diffusion models for ECG generation on the minute scale. *Computer Methods and Programs in Biomedicine*. https://doi.org/10.1016/j.cmpb.2025.109138 — *not downloaded*
- **P075** Xinyu Tian, Sio Kei Im, Kefeng Li et al. (2026). Exploring multimodal generative approaches in cardiovascular disease: A five-year systematic literature review. *Array*. https://doi.org/10.1016/j.array.2026.101276 — *not downloaded*
- **P076** Nathan C. L. Kong, Dae Lee, Huyen Do et al. (2024). f-GAN: A frequency-domain-constrained generative adversarial network for PPG to ECG synthesis. *arXiv*. https://doi.org/10.48550/arxiv.2406.16896
- **P077** Vitalii Bondar, Serhii Semenov, Vira Babenko et al. (2025). FlowECG: Using Flow Matching to Create a More Efficient ECG Signal Generator. *arXiv*. https://doi.org/10.1007/978-3-032-18415-3_32
- **P078** Anisha Riya, Abdullah Bin Queyam (2025). Generating High-Fidelity Synthetic ECG Signals Using Deep Autoencoder Architectures. *n/a*. https://doi.org/10.1109/aists66100.2025.11232714 — *not downloaded*
- **P079** Hyeon-Hwa Choi, Segyeong Joo (2023). Generating Precordial-lead Electrocardiogram from Smartwatch. *Computing in cardiology*. https://doi.org/10.22489/cinc.2023.083
- **P080** Paul Pöhl, Viktor Schlegel, Hao Li et al. (2025). Generating Realistic Multi-Beat ECG Signals. *arXiv*. https://doi.org/10.1109/dsp65409.2025.11074944
- **P081** Bertan Karahoda (2024). Generating Time Series Data With Real-Valued DC-GAN From Complex Time-Frequency Domain: Application to ECG Synthesis. *IEEE Access*. https://doi.org/10.1109/access.2024.3469541 — *not downloaded*
- **P082** Chaoying Jiang, Yujing Xin, Ning Liu et al. (2025). Generation and Selection: A Self-Iterative Two-Stage Data Augmentation Method for Automated ECG Classification. *IEEE Journal of Biomedical and Health Informatics*. https://doi.org/10.1109/jbhi.2025.3611429 — *not downloaded*
- **P083** Qi Zhang, Hongyan Li (2026). Generation of Realistic Synthetic ECG Data Using Uncertainty-Aware Diffusion Model. *Lecture notes in computer science*. https://doi.org/10.1007/978-3-032-22267-1_25 — *not downloaded*
- **P084** Panteleimon Pantelidis, Evangelos K. Oikonomou, Maria Bampa et al. (2024). Generative adversarial networks (GANs) to produce synthetic 12-lead electrocardiogram signals for specific and rare diseases: a novel, powerful tool towards clinical advancements. *European Heart Journal*. https://doi.org/10.1093/eurheartj/ehae666.3427 — *not downloaded*
- **P085** Jiaqi Liang, Yuheng Zhou, Kai Ma et al. (2026). Generative Adversarial Networks for Modeling Bio-Electric Fields in Medicine: A Review of EEG, ECG, EMG, and EOG Applications. *Bioengineering*. https://doi.org/10.3390/bioengineering13010084
- **P086** Yousef Nademi, Sunil V. Kalmady, Weijie Sun et al. (2023). Generative Data by β-Variational Autoencoders Help Build Stronger Classifiers: ECG Use Case. *International Symposium on Medical Information Processing and Analysis (SIPAIM)*. https://doi.org/10.1109/sipaim56729.2023.10373478 — *not downloaded*
- **P087** Skoric J, D'Mello Y, Plant DV. (2025). Generative Reconstruction of Multimodal Cardiac Waveforms From a Single Vibrational Cardiography Sensor. *IEEE journal of biomedical and health informatics*. https://doi.org/10.1109/jbhi.2025.3561071 — *not downloaded*
- **P088** Yongjun Yoo (2026). Graph-Based ECG Synthesis with Activation-Consistency Certification and Diagnostics-Aware Morphology Curation. *arXiv*. https://doi.org/10.48550/arxiv.2606.26580
- **P089** Zhuoyi Huang, Nutan Sahoo, Anamika Kumari et al. (2025). High-Fidelity Synthetic ECG Generation via Mel-Spectrogram Informed Diffusion Training. *arXiv*. https://doi.org/10.48550/arxiv.2510.05492
- **P090** Aron Jose A, A. Shamila Ebenezer (2026). Hybrid Quantum-Classical Generative Adversarial Network for Synthetic 12-Lead Electrocardiogram Signal Generation. *n/a*. https://doi.org/10.1109/iecct68664.2026.11541994 — *not downloaded*
- **P091** Nour Neifar, Achraf Ben Hamadou (2025). Implicit Neural Representations for ECG Synthesis: What is the Potential ?. *IEEE/ACS International Conference on Computer Systems and Applications (AICCSA)*. https://doi.org/10.1109/aiccsa66935.2025.11315421 — *not downloaded*
- **P092** Ruby Narula, Neha Goyal (2025). Improving Diagnostic Performance through Synthetic Beat Generation: A Hybrid Framework Combining Undersampling and Generative Oversampling for Balanced ECG Learning. *IEEE Global Conference for Advancement in Technology (GCAT)*. https://doi.org/10.1109/gcat66372.2025.11368449 — *not downloaded*
- **P093** Alexander Jenkins, Zehua Chen, Fu Siong Ng et al. (2023). Improving Diffusion Models for ECG Imputation with an Augmented Template Prior. *arXiv*. https://doi.org/10.48550/arxiv.2310.15742
- **P094** Zanchi B, Monachino G, Metaldi M et al. (2026). Introducing a Comprehensive Framework for Synthetic ECG Validation. *IEEE open journal of engineering in medicine and biology*. https://doi.org/10.1109/ojemb.2026.3716291
- **P095** Sara Battiston, Roberto Sassi, Massimo Walter Rivolta (2025). Invertible Conditional Generative Adversarial Networks to Effectively Generate Myocardial Infarction from Normal ECG. *n/a*. https://doi.org/10.1109/embc58623.2025.11253299 — *not downloaded*
- **P096** Gabriel B. Moro, Joaquim Assunção, Isabel Cristina Reinheimer et al. (2025). Investigating Transformer-Based GANs for Realistic ECG Time-Series Data Generation. *IEEE International Symposium on Computer-Based Medical Systems (CBMS)*. https://doi.org/10.1109/cbms65348.2025.00038 — *not downloaded*
- **P097** Jian Tan, Xinrui Qiu, Zhanshuo Shang et al. (2026). L2L-ESN: A Lead-to-Lead Electrocardiogram Synthesis Network for Assisting Myocardial Infarction Diagnosis. *Intelligent Computing*. https://doi.org/10.34133/icomputing.0768 — *not downloaded*
- **P098** Yue Li, Mikhail Gur'evich Poluektov, Álan Luiz Éckeli et al. (2026). Latent diffusion based hard sample generation for obstructive sleep apnea detection using single-lead ECG. *IET conference proceedings.*. https://doi.org/10.1049/icp.2026.2739 — *not downloaded*
- **P099** Nour Neifar, Achraf Ben Hamadou, Afef Mdhaffar et al. (2024). Leveraging Statistical Shape Priors in GAN-Based ECG Synthesis. *IEEE Access*. https://doi.org/10.1109/access.2024.3373724
- **P100** Lehuai Xu, Zirui Lu, Haoran Yang et al. (2025). Lightweight Multi-task CNN for ECG Diagnosis with GRU-Diffusion. *arXiv*. https://doi.org/10.48550/arxiv.2511.14104
- **P101** Wen H, Chang S, Zhou L et al. (2026). MAGIC: Multi-Grained Conditional Diffusion for High-Fidelity PPG-to-ECG Translation. *IEEE journal of biomedical and health informatics*. https://doi.org/10.1109/jbhi.2026.3713977 — *not downloaded*
- **P102** Yanhao Huang, Shibo Feng, Wanjin Feng et al. (2026). MedFlow: Class-Aware Multi-Scale Generation for Medical Time-Series Synthesis. *arXiv*. https://doi.org/10.48550/arxiv.2609.04804
- **P103** Tiwari A, Kishore J, Singh R. (2026). Minority class-aware multiclass arrhythmia detection using conditional GAN augmentation. *Scientific reports*. https://doi.org/10.1038/s41598-026-51237-z
- **P104** Qian Shao, Bang Du, Zepeng Li et al. (2025). MM-DADM: Multimodal Drug-Aware Diffusion Model for Virtual Clinical Trials. *arXiv*. https://doi.org/10.48550/arxiv.2502.07297
- **P105** Lei Zhang, Cheng Su, Mengying Ou et al. (2026). MorphDiff-ECG: A Diffusion Model for Multimodal Feature Fusion of ECG Signals. *IEEE Transactions on Biomedical Engineering*. https://doi.org/10.1109/tbme.2026.3735103 — *not downloaded*
- **P106** Sepahvand M, Dourgham Karim Al-Harizi B, Meqdad MN. (2026). Morphology-preserving transfer-guided GAN with adaptive discriminative loss for robust and imbalanced ECG arrhythmia detection. *Computers in biology and medicine*. https://doi.org/10.1016/j.compbiomed.2026.111862 — *not downloaded*
- **P107** Yakir Yehuda, Kira Radinsky (2024). ODE-Constrained Generative Modeling of Cardiac Dynamics for 12-Lead ECG Synthesis. *arXiv*. https://doi.org/10.48550/arxiv.2409.17833
- **P108** Evgeniy Schetinin, Anna V. Pestryakova, Julia Georgievna Shatalova et al. (2026). On the generation of 12-channel electrocardiograms based on a hybrid of diffusion and graph neural network models. *VESTNIK OF ASTRAKHAN STATE TECHNICAL UNIVERSITY SERIES MANAGEMENT COMPUTER SCIENCE AND INFORMATICS*. https://doi.org/10.24143/2072-9502-2026-2-15-22 — *not downloaded*
- **P109** Xinyi Wu, Zouheir Rezki, Bhavan Balusu et al. (2025). One model, dual tasks: a novel distributionally adaptive learning framework for ECG classification and generation addressing intra- and inter-patient variability. *Expert Systems with Applications*. https://doi.org/10.1016/j.eswa.2025.130096 — *not downloaded*
- **P110** Максим Михайлович Гордеев, A.E. Savkin, O. P. Timofeeva et al. (2026). Optimization of generative-adversarial networks for the synthesis of electrocardiograms by adaptive quantization. *Herald of Dagestan State Technical University Technical Sciences*. https://doi.org/10.21822/2073-6185-2026-53-2-52-60
- **P111** Yakir Yehuda, Kira Radinsky (2026). PDE-Driven Spatiotemporal Generative Modeling for Multilead ECG Synthesis. *Proceedings of the AAAI Conference on Artificial Intelligence*. https://doi.org/10.1609/aaai.v40i2.37120
- **P112** Shuntaro Suzuki, Shuitsu Koyama, Shinnosuke Hirano et al. (2026). PENGUIN: General Vital Sign Reconstruction from PPG with Flow Matching State Space Model. *arXiv*. https://doi.org/10.1109/icassp55912.2026.11463201
- **P113** Jonas Lynggaard Isaksen, Vajira Lasantha Thambawita, Malene Nørregaard et al. (2025). Personalized Synthetic Electrocardiograms with Outcomes. *medRxiv*. https://doi.org/10.1101/2025.08.01.25332716
- **P114** Xiaoda Wang, Minxiao Wang, Kaiqiao Han et al. (2026). PG-LRF: Physiology-Guided Latent Rectified Flow for Electro-Hemodynamic PPG-to-ECG Generation. *arXiv*. https://doi.org/10.48550/arxiv.2605.12541
- **P115** Stobak Dutta, Amartya Chakraborty, Anirban Mitra et al. (2026). PHYSIGEN: Physiological signal generation for class imbalance mitigation based on generative AI and machine learning. *Innovation and Emerging Technologies*. https://doi.org/10.1142/s2737599426400025 — *not downloaded*
- **P116** Yating Hu, Yu Lu, Wei Zhang et al. (2026). Physiology-Aware Benchmarking of Deep Generative Models for Fetal ECG Synthesis. *Lecture notes in computer science*. https://doi.org/10.1007/978-981-92-3441-7_35 — *not downloaded*
- **P117** Khuong Vo, Mostafa El‐Khamy, Yoojin Choi (2024). PPG-to-ECG Signal Translation for Continuous Atrial Fibrillation Detection via Attention-based Deep State-Space Modeling. *n/a*. https://doi.org/10.1109/embc53108.2024.10781630
- **P118** Xiaocheng Fang, Jiarui Jin, Haoyu Wang et al. (2025). PPGFlowECG: Latent Rectified Flow with Cross-Modal Encoding for PPG-Guided ECG Generation and Cardiovascular Disease Detection. *arXiv*. https://arxiv.org/abs/2509.19774
- **P119** Chao Tang (2025). Principal component conditional generative adversarial networks for imbalanced ECG classification enhancement. *PLoS ONE*. https://doi.org/10.1371/journal.pone.0330707
- **P120** Georgios Kritopoulos, Georgios Neofotistos, Georgios D. Barmparis et al. (2026). Quantum-Refined Latent Diffusion: A Hybrid Generative Framework for Imbalanced ECG Classification. *medRxiv*. https://doi.org/10.64898/2026.04.09.26350502
- **P121** Mingjun Lin, Xin Zhang, Yong Hong et al. (2025). RDiffGAN-ECG: High-quality specific R-peaks conditional ECG generation using denoising diffusion generative adversarial network with state space models. *Biomedical Signal Processing and Control*. https://doi.org/10.1016/j.bspc.2025.108544 — *not downloaded*
- **P122** Banafsheh Adami, Nima Karimian, Jeremy Michael Dawson (2025). rECG: A Guided Diffusion Framework for Remote Electrocardiography Reconstruction from Facial Video. *IEEE International Joint Conference on Biometrics (IJCB)*. https://doi.org/10.1109/ijcb65343.2025.11410969 — *not downloaded*
- **P123** Xinyan Guan, Yongfan Lai, Jiarui Jin et al. (2025). Reconstructing 12-Lead ECG from 3-Lead ECG using Variational Autoencoder to Improve Cardiac Disease Detection of Wearable ECG Devices. *arXiv*. https://doi.org/10.1371/journal.pdig.0001335
- **P124** Lisa Bedin, Yazid Janati, Gabriel Victorino Cardoso et al. (2025). Reconstructing ECG from indirect signals: a denoising diffusion approach. *Philosophical Transactions of the Royal Society A Mathematical Physical and Engineering Sciences*. https://doi.org/10.1098/rsta.2024.0330 — *not downloaded*
- **P125** Hong Chen, Jing Zhan, Rui Feng et al. (2025). Reconstruction of ECG from ballistocardiogram using generative adversarial networks with attention. *Biomedical Physics & Engineering Express*. https://doi.org/10.1088/2057-1976/adbbf5 — *not downloaded*
- **P126** Debaditya Shome, Pritam Sarkar, Ali Etemad (2024). Region-Disentangled Diffusion Model for High-Fidelity PPG-to-ECG Translation. *Proceedings of the AAAI Conference on Artificial Intelligence*. https://doi.org/10.1609/aaai.v38i13.29422
- **P127** Shuenn-Yuh Lee, Kai-Ze Lei, Ju-Yi Chen et al. (2026). ReHeartNet: Reconstruct Electrocardiogram From Photoplethysmography by Using Dense Connected Deep Learning Model. *IEEE Open Journal of Engineering in Medicine and Biology*. https://doi.org/10.1109/ojemb.2026.3670010
- **P128** Dawei Li, Tienan Chen, Cong Liu et al. (2025). Semi-supervised GAN for enhancing electrocardiogram time series diagnostics. *Biomedical Signal Processing and Control*. https://doi.org/10.1016/j.bspc.2025.108058 — *not downloaded*
- **P129** Kim J, Park K, Chen L et al. (2026). Shape and amplitude decoupling in pulsatile physiological signal synthesis and its evaluation. *Nature communications*. https://doi.org/10.1038/s41467-026-72299-7
- **P130** Xiaoda Wang, Kaiqiao Han, Yuhao Xu et al. (2025). Simulator and Experience Enhanced Diffusion Model for Comprehensive ECG Generation. *arXiv*. https://doi.org/10.48550/arxiv.2511.09895
- **P131** Zhang Y, Xia Y. (2026). Single-Lead ECG Arrhythmia Classification Based on Peak-Enhanced Attention Network and Quality-Aware GAN Data Augmentation Framework. *Sensors (Basel, Switzerland)*. https://doi.org/10.3390/s26123852
- **P132** Jiaqi Liang, Ruizhe Wang, Zhanyi Liu et al. (2026). SMA-GAN: A Physiology-Guided Adversarial Network with Attention and Spectral Constraints for Imbalanced ECG Synthesis. *IEEE International Conference on Acoustics Speech and Signal Processing*. https://doi.org/10.1109/icassp55912.2026.11463430 — *not downloaded*
- **P133** Ashutosh Mishra, Nicolas Stein, Louis Peter et al. (2026). Spatially-Conditioned Variational Autoencoder with Latent Manifold Harvesting for High-Fidelity 12-Lead ECG Synthesis. *Research Square*. https://doi.org/10.21203/rs.3.rs-9222289/v1
- **P134** Sergey Skorik, Aram Avetisyan (2024). SSSD-ECG-nle: New Label Embeddings with Structured State-Space Models for ECG generation. *arXiv*. https://doi.org/10.1109/ivmem63006.2024.10659391
- **P135** J Hesp, Wouter A. C. van Amsterdam, Maarten van Smeden (2026). Style translation of simulated ECGs to realistic ECGs with generative adversarial networks for data-scarce clinical settings: challenges and opportunities. *European Heart Journal - Digital Health*. https://doi.org/10.1093/ehjdh/ztaf143.131
- **P136** Ioana Crețu, Alexander Tindale, Wamadeva Balachandran et al. (2024). Synthesis of Multimodal Cardiological Signals Using a Conditional Wasserstein Generative Adversarial Network. *IEEE Access*. https://doi.org/10.1109/access.2024.3449134 — *not downloaded*
- **P137** Gianmarco Parise, Roberto Ceravolo, Fabiana Lucà et al. (2026). Synthetic artificial intelligence in cardiology: from generative models to clinical applications. *European Heart Journal Open*. https://doi.org/10.1093/ehjopen/oeag026
- **P138** Muhammed Halil Akpınar, Abdulkadir Şengür, Massimo Salvi et al. (2024). Synthetic Data Generation via Generative Adversarial Networks in Healthcare: A Systematic Review of Image- and Signal-Based Studies. *IEEE Open Journal of Engineering in Medicine and Biology*. https://doi.org/10.1109/ojemb.2024.3508472
- **P139** José Fernando Núñez, Jamie Arjona, Javier Béjar (2024). Synthetic ECG Generation for Data Augmentation and Transfer Learning in Arrhythmia Classification. *arXiv*. https://doi.org/10.48550/arxiv.2411.18456
- **P140** Edmond Adib, Fatemeh Afghah, John Jeffery Prevost (2025). Synthetic ECG signal generation using generative neural networks. *PLoS ONE*. https://doi.org/10.1371/journal.pone.0271270
- **P141** Zanchi B, Monachino G, Fiorillo L et al. (2025). Synthetic ECG signals generation: A scoping review. *Computers in biology and medicine*. https://doi.org/10.1016/j.compbiomed.2024.109453 — *not downloaded*
- **P142** Giovanny Barbosa‐Casanova, Norelli Schettini, Winston Percybrooks et al. (2025). Synthetic Electrocardiogram Spectrogram Generation Using Generative Adversarial Network‐Based Models: A Comparative Study. *Advanced Intelligent Systems*. https://doi.org/10.1002/aisy.202500705
- **P143** Beatrice Zanchi, Giuliana Monachino, Francesca Dalia Faraci et al. (2025). Synthetic electrocardiograms for Brugada syndrome: from data generation to expert cardiologists evaluation. *European Heart Journal - Digital Health*. https://doi.org/10.1093/ehjdh/ztaf039
- **P144** Cattozzo F, Battiston S, Rivolta MW et al. (2025). Text-to-ECG: a Framework to Generate 12-Lead ECG from Text Reports. *Annual International Conference of the IEEE Engineering in Medicine and Biology Society. IEEE Engineering in Medicine and Biology Society. Annual International Conference*. https://doi.org/10.1109/embc58623.2025.11254939 — *not downloaded*
- **P145** Maria Russo, Joana Rebelo, Nuno Bento et al. (2025). Towards High-Fidelity ECG Generation: Evaluation via Quality Metrics and Human Feedback. *International Joint Conference on Biomedical Engineering Systems and Technologies (BIOSTEC)*. https://doi.org/10.5220/0013400500003911 — *not downloaded*
- **P146** Yuxin Lin, Jing Ma, Suyu Dong et al. (2025). TransDiffECG: Semantically controllable ECG synthesis via transformer-based diffusion modeling. *Journal of Biomedical Informatics*. https://doi.org/10.1016/j.jbi.2025.104948 — *not downloaded*
- **P147** Ayswarya R Kurup, Mithun Kumar Kar, Madhusudhan Mishra et al. (2026). Transformer-Based Generative Adversarial Network With Multi-Scale Temporal Attention for ECG Synthesis and PQRST Feature Preservation. *IEEE Access*. https://doi.org/10.1109/access.2026.3656370 — *not downloaded*
- **P148** Omer Belhasin, Idan Kligvasser, George Leifman et al. (2024). Uncertainty-Aware PPG-2-ECG for Enhanced Cardiovascular Diagnosis using Diffusion Models. *arXiv*. https://doi.org/10.48550/arxiv.2405.11566
- **P149** Jiarui Jin, Haoyu Wang, Xiang Lan et al. (2025). UniECG: Understanding and Generating ECG in One Unified Model. *arXiv*. https://doi.org/10.48550/arxiv.2509.18588
- **P150** N. Moniz Cordova, I. Fernández Cañedo, Luis Hernández-Álvarez (2025). User Authentication Breakdown: Fake Electrocardiogram Signals with Generative AI. *DIGITAL.CSIC (Spanish National Research Council (CSIC))*.  — *not downloaded*
- **P151** Ryo Nishikimi, Masahiro Nakano, Kunio Kashino et al. (2023). Variational autoencoder–based neural electrocardiogram synthesis trained by FEM-based heart simulator. *Cardiovascular Digital Health Journal*. https://doi.org/10.1016/j.cvdhj.2023.12.002
- **P152** Zehua Chen, Yuyang Miao, Liyuan Wang et al. (2025). Versatile Cardiovascular Signal Generation with a Unified Diffusion Transformer. *arXiv*. https://doi.org/10.48550/arxiv.2505.22306
- **P153** Skoric, James (2025). Wearable health monitoring with seismocardiography and generative modeling. *eScholarship@McGill (McGill)*. https://doi.org/10.82308/39516 — *not downloaded*
- **P154** Farhana Ahmed Chowdhury, Farhana Ahmed Chowdhury, Md. Kamal Hosain et al. (2024). ECG waveform generation from radar signals: A deep learning perspective. *Computers in Biology and Medicine*. https://doi.org/10.1016/j.compbiomed.2024.108555 — *not downloaded*
- **P155** Qi Zhang, Hongyan Li (2025). Uncertainty‐Guided Diffusion Model for High‐Fidelity ECG Synthesis and Classification. *Expert Systems*. https://doi.org/10.1111/exsy.70070 — *not downloaded*
- **P156** Rongjia Wang, Yihai Fang, Jianhong Dou et al. (2025). Diff-TTE: A Novel Diffusion Model for Text-to-Electrocardiogram. *International Conference on Electronic Information Engineering and Computer Technology (EIECT)*. https://doi.org/10.1109/eiect68017.2025.11331862 — *not downloaded*
- **P157** Yuxin Lin, Jing Ma, Wei Wang et al. (2024). Biomedically Informed ECG Synthesis: Customizing Cardiac Cycle Phases with Diffusion Model. *IEEE International Conference on Bioinformatics and Biomedicine (BIBM)*. https://doi.org/10.1109/bibm62325.2024.10821878 — *not downloaded*
- **P158** Majid Sepahvand, Maytham N. Meqdad (2026). Coarse-to-fine generative augmentation and cross-modal physiological fusion for imbalanced ECG arrhythmia detection. *Intelligence-Based Medicine*. https://doi.org/10.1016/j.ibmed.2026.100457 — *not downloaded*
- **P159** Sujit Bhandari, Robin Chataut (2026). Physiologically Validated Synthetic ECG Generation via LLM-Guided Constraint Enforcement. *Lecture notes in computer science*. https://doi.org/10.1007/978-3-032-39379-1_19 — *not downloaded*
- **P160** Marko Miletic, Murat Sariyar (2026). Temporal Latent Priors Improve Sequential Generative Modeling of Full-Length 12-Lead ECGs. *IEEE International Symposium on Computer-Based Medical Systems (CBMS)*. https://doi.org/10.1109/cbms69103.2026.00024 — *not downloaded*
- **P161** Theekshana Dissanayake, Tharindu Fernando, Simon Denman et al. (2026). Continuous multi-step ECG and PPG generation through latent disentanglement. *Computers in Biology and Medicine*. https://doi.org/10.1016/j.compbiomed.2026.111996 — *not downloaded*
- **P162** Peng Zhao, Si Shi, Fei Richard Yu et al. (2026). SpectroMamba Flow Matching (SMFM): Fast ECG Generation via 2D Dual-Channel Spectrograms. *IEEE International Conference on Acoustics Speech and Signal Processing*. https://doi.org/10.1109/icassp55912.2026.11464731 — *not downloaded*
- **P163** Jingwei Liu, Hongyan Li, Shenda Hong (2024). Synthesis of Standard 12-Lead ECG from Single-Lead ECG Using Shifted Diffusion Models. *Lecture notes in computer science*. https://doi.org/10.1007/978-3-031-70378-2_17 — *not downloaded*
- **P164** Guangqi Chen, Fan Lin, Yuhang Liu et al. (2025). Progressive Two-Stage ECG Signal Generation: From Structural Skeletons to High-Fidelity Detail Refinement. *IEEE International Conference on Bioinformatics and Biomedicine (BIBM)*. https://doi.org/10.1109/bibm66473.2025.11357105 — *not downloaded*
- **P165** Debapriya Hazra, Yung-Cheol Byun (2020). SynSigGAN: Generative Adversarial Networks for Synthetic Biomedical Signal Generation. *Biology*. https://doi.org/10.3390/biology9120441 *(background)*
- **P166** Vajira Lasantha Thambawita, Jonas Lynggaard Isaksen, Steven Alexander Hicks et al. (2021). DeepFake electrocardiograms using generative adversarial networks are the beginning of the end for privacy issues in medicine. *Scientific Reports*. https://doi.org/10.1038/s41598-021-01295-2 *(background)*
- **P167** Edmonmd Adib, Amanda S. Fernandez, Fatemeh Afghah et al. (2023). Synthetic ECG Signal Generation Using Probabilistic Diffusion Models. *IEEE Access*. https://doi.org/10.1109/access.2023.3296542 *(background)*
- **P168** Juan Miguel Lopez Alcaraz, Nils Strodthoff (2023). Diffusion-based conditional ECG generation with structured state space models. *Computers in Biology and Medicine*. https://doi.org/10.1016/j.compbiomed.2023.107115 *(background)*
- **P169** Jintai Chen, Kuanlun Liao, Wei, Kun et al. (2022). ME-GAN: Learning Panoptic Electrocardio Representations for Multi-view ECG Synthesis Conditioned on Heart Diseases. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2207.10670 *(background)*
- **P170** Nour Neifar, Afef Mdhaffar, Achraf Ben Hamadou et al. (2023). Deep Generative Models for Physiological Signals: A Systematic Literature Review. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2307.06162 *(background)*
- **P171** Laurenz Berger, Max Haberbusch, Francesco Moscato (2023). Generative adversarial networks in electrocardiogram synthesis: Recent developments and challenges. *Artificial Intelligence in Medicine*. https://doi.org/10.1016/j.artmed.2023.102632 *(background)* — *not downloaded*
- **P172** Tomer Golany, Daniel Freedman, Kira Radinsky (2021). ECG ODE-GAN: Learning Ordinary Differential Equations of ECG Dynamics via Generative Adversarial Learning. *Proceedings of the AAAI Conference on Artificial Intelligence*. https://doi.org/10.1609/aaai.v35i1.16086 *(background)*
- **P173** Eoin Brophy, Maarten De Vos, Geraldine B. Boylan et al. (2021). Multivariate Generative Adversarial Networks and Their Loss Functions for Synthesis of Multichannel ECGs. *IEEE Access*. https://doi.org/10.1109/access.2021.3130421 *(background)*
- **P174** Hyunseung Chung, Jiho Kim, Joon‐myoung Kwon et al. (2023). Text-to-ECG: 12-Lead Electrocardiogram Synthesis Conditioned on Clinical Text Reports. *IEEE International Conference on Acoustics Speech and Signal Processing*. https://doi.org/10.1109/icassp49357.2023.10096898 *(background)*
- **P175** Subhrajyoti Dasgupta, Sudip Kumar Das, Ujjwal Bhattacharya (2021). CardioGAN: An Attention-based Generative Adversarial Network for Generation of Electrocardiograms. *Proceedings - International Conference on Pattern Recognition/Proceedings/International Conference on Pattern Recognition*. https://doi.org/10.1109/icpr48806.2021.9412905 *(background)* — *not downloaded*
- **P176** Nour Neifar, Afef Mdhaffar, Achraf Ben-Hamadou et al. (2022). Disentangling temporal and amplitude variations in ECG synthesis using anchored GANs. *ACM/SIGAPP Symposium on Applied Computing (SAC)*. https://doi.org/10.1145/3477314.3507300 *(background)* — *not downloaded*
- **P177** Xiaomin Li, Mykhailo Sakevych, Gentry Atkinson et al. (2024). BioDiffusion: A Versatile Diffusion Model for Biomedical Signal Synthesis. *Bioengineering*. https://doi.org/10.3390/bioengineering11040299
- **P178** Yaojun Hu, Jintai Chen, Lianting Hu et al. (2024). Personalized Heart Disease Detection via ECG Digital Twin Generation. *n/a*. https://doi.org/10.24963/ijcai.2024/649
- **P179** unverified (University of Waterloo MSc thesis) (2026). A Comprehensive Evaluation Framework for Synthetic ECG: Assessing Fidelity, Utility, and Privacy. *UWSpace (thesis)*. https://uwspace.uwaterloo.ca/items/0fff9cd3-cb39-4e3a-b81d-2ade38b1dd22/full — *not downloaded*
