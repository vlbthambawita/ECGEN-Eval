# Cross-check against `literature_review_codex/`

Date: 2026-10-26. This compares my review (`papers_index.csv`, P001–P186) with the independent review in
`../literature_review_codex/` (53 screened studies, 35 included with full text) and checks
whether each paper really belongs in the review.

## Summary

| | Count |
|---|---:|
| Codex studies (screening log) | 53 |
| Already in my list | 50 |
| **Missed by me, now added** (P180 P2Es, P181 CoFE, P183 cGAN presentation attacks) | 3 |
| PDFs the codex review had but I did not (copied: P145, P179, P180, P181) | 4 |
| Disagreements on inclusion (P009, P048, P119) | 3 |
| **Excluded after full-text re-check** (P048) | 1 |
| **Further misses found by re-scanning my own keyword-excluded titles** (P182, P184, P185, P186) | 4 |

Net effect: the review now has **185 included papers** (173 from Oct 2023 – Oct 2026 + 12 background).
**95** of them have full text and are in the Paper Database (was 91: +5 new, −1 excluded).

## Why papers were missed

Two of the three codex-only papers (P2Es, CoFE) were in my search results but were dropped by the
automatic keyword pre-filter ("no generative term"). I re-scanned all 870 titles that filter dropped
for generative-model words (98 hits) and checked each by hand. Four more in-scope papers turned up
(P182, P184, P185, P186). The rest were correctly excluded: report/text generation, denoising,
anomaly detection, and deterministic regression-based reconstruction, which my plan excludes
(e.g. *ImputeECG*, *Deep Spectra P2E*). The third paper (P183, EMBC 2025) was not returned by
any of my queries.

## Newly added papers

| ID | Paper | Model | Full text | File / where to get it |
|---|---|---|---|---|
| P180 | Ji et al. 2026, *P2Es: Physiology-conditioned diffusion for 12-lead ECG generation from PPG*, Smart Health | Diffusion | yes (arXiv v1, titled "Translation from Wearable PPG to 12-Lead ECG") | `papers/03_Diffusion/2026_Ji_P2Es_Physiology_Conditioned_Diffusion_12_Lead_PPG.pdf` |
| P181 | Jang et al. 2025, *CoFE: A Framework Generating Counterfactual ECG for Explainable Cardiac AI-Diagnostics*, arXiv | GAN (StyleGAN2 + inversion) | yes | `papers/01_GAN/2025_Jang_CoFE_Counterfactual_ECG_Explainable_Cardiac.pdf` |
| P182 | Kamel et al. 2026, *BeatFlow-ECG: Rectified Flow for ECG Reconstruction from Indirect Wearable Signals*, arXiv | Rectified flow | yes | `papers/04_Flow_Matching_and_Normalizing_Flows/2026_BeatFlow_ECG_Rectified_Flow_ECG_Reconstruction_Wearable.pdf` |
| P183 | Wang et al. 2025, *Presentation Attacks on the PCA-Based Biometric System Using cGAN-Generated ECGs*, EMBC | cGAN | **no** (not open access) | https://doi.org/10.1109/embc58623.2025.11253493 |
| P184 | Zhu et al. 2025, *Diffusion-based high dimensional subspace mapping for ECG generation with structured state space models*, Applied Intelligence | Diffusion + S4 | **no** | https://doi.org/10.1007/s10489-025-06640-w |
| P185 | Li et al. 2025, *Radar2ECG: … Conditional Electrocardiogram Generation from Radar Heart Sound*, ICASSP | Autoencoder-based; generative status to confirm | **no** | https://doi.org/10.1109/icassp49660.2025.10888884 |
| P186 | Nazami et al. 2026, *Structure-preserving adversarial multi-segment framework for bidirectional ECG–SCG signal translation*, BSPC | GAN | **no** | https://doi.org/10.1016/j.bspc.2026.110999 |

Papers that already had IDs but whose PDFs were copied from the codex folder:

- **P145:** Russo, *Towards High-Fidelity ECG Generation…*. The file is the author's Dec 2024 MSc thesis (NOVA Lisbon), which the 2025 BIOSTEC paper is based on. Saved as `papers/07_Evaluation_Methods_and_Benchmarks/2024_Russo_thesis_Towards_High_Fidelity_ECG_Generation.pdf`. The published paper is still worth getting.
- **P179:** Yixin Li, *A Comprehensive Evaluation Framework for Synthetic ECG: Assessing Fidelity, Utility, and Privacy* (Waterloo MSc thesis, 2026). It covers TSTR/TRTR, ACF/PSD/DTW-ratio/DWT fidelity, DCR/NNDR and seven membership-inference attacks.

P183–P186 are in `to_download.md` with their *Save as* names. Their `papers_index.csv` rows are abstract-level only.

## Validity of the disagreements

| ID | Paper | Codex | Mine (before) | Verdict |
|---|---|---|---|---|
| P048 | Zhou 2025, *DiffECG: Diffusion Model-Powered Label-Efficient and Personalized Arrhythmia Diagnosis* | exclude | include | Codex is right. The diffusion model is used only for self-supervised representation learning on Lorenz-plot images, and no synthetic ECGs are generated or evaluated. **Excluded now**: marked `EXCLUDED` in `papers_index.csv` and skipped by `build_db.py`. |
| P119 | Tang 2025, *Principal component conditional GANs for imbalanced ECG classification* (PLOS ONE) | exclude ("feature-coefficient augmentation only") | include | **Codex is wrong.** The GAN generates PCA coefficients that are reconstructed into waveforms, and these are evaluated with NPRD/NRMSE/NMAE, Wasserstein distance, JS divergence and a KS test against TD-GAN, TimeGAN and conditional DDPM. Kept. |
| P009 | Speziale 2026, *A Usable GAN-Based Tool for Synthetic ECG Generation in Cardiac Amyloidosis Research* | exclude ("protocol only") | include | Both are right on the facts: the evaluation is planned but not run. Kept because the planned protocol is relevant (DTW, Fréchet, productivity rate); the metrics are already flagged "Planned only". |

## Metadata checks

- **P123 (Guan, WearECG):** the codex review cites the 2026 PLOS Digital Health version (doi 10.1371/journal.pdig.0001335); my row keeps the 2025 arXiv year. Same paper.
- **P151 (Nishikimi):** the codex review gives 2024, but it was published 2023-12-22. My year is correct.
- **P180:** the arXiv v1 PDF has a different title from the published *P2Es* paper. The published version has a PMC author manuscript (PMC13459857) but no PDF in the PMC open-data bucket.
- No metadata errors were found for the other 47 matched papers. Titles and DOIs/arXiv IDs agree.

## Borderline, not added

- Zubair et al. 2023, *Deep Representation Learning With Sample Generation and Augmented Attention Module for Imbalanced ECG Classification* (IEEE JBHI, doi 10.1109/jbhi.2023.3325540). It turns majority-class samples into minority-class samples with a translation loss, and it is not clear this is a generative model. The open-access IEEE PDF blocked scripted download. If you download it, I can decide from the full text.

## Paper-by-paper comparison (all 53 codex studies)

| Codex ID | Title | Codex decision | My ID | My status now | Verdict |
|---|---|---|---|---|---|
| Nunez_2024_Augmentation | Synthetic ECG Generation for Data Augmentation and Transfer Learning in Arrhythm | include | P139 | full text | Agree |
| Speziale_2026_Amyloidosis | A Usable GAN-Based Tool for Synthetic ECG Generation in Cardiac Amyloidosis Rese | exclude | P009 | full text | Both correct on the facts: the evaluation is only planned. Kept, with metrics flagged "Planned only". |
| Huang_2025_MIDT | High-Fidelity Synthetic ECG Generation via Mel-Spectrogram Informed Diffusion Tr | include | P089 | full text | Agree |
| Pohl_2025_MultiBeat | Generating Realistic Multi-Beat ECG Signals | include | P080 | full text | Agree |
| Bondar_2025_FlowECG | FlowECG: Using Flow Matching to Create a More Efficient ECG Signal Generator | include | P077 | full text | Agree |
| Yehuda_2024_MultiODE | ODE-Constrained Generative Modeling of Cardiac Dynamics for 12-Lead ECG Synthesi | include | P107 | full text | Agree |
| Sviridov_2025_cNVAE | Conditional Electrocardiogram Generation Using Hierarchical Variational Autoenco | include | P038 | full text | Agree |
| Oladunni_2026_Complementarity | Complementarity-Preserving Generative Theory for Multimodal ECG Synthesis: A Qua | include | P036 | full text | Agree |
| Skorik_2024_SSSDnle | SSSD-ECG-nle: New Label Embeddings with Structured State-Space Models for ECG ge | include | P134 | full text | Agree |
| Lai_2025_ECGTwin | ECGTwin: Personalized ECG Generation Using Controllable Diffusion Model | include | P067 | full text | Agree |
| Wang_2025_SEDiff | Simulator and Experience Enhanced Diffusion Model for Comprehensive ECG Generati | include | P130 | full text | Agree |
| Jin_2025_UniECG | UniECG: Understanding and Generating ECG in One Unified Model | include | P149 | full text | Agree |
| Wang_2026_PGLRF | PG-LRF: Physiology-Guided Latent Rectified Flow for Electro-Hemodynamic PPG-to-E | include | P114 | full text | Agree |
| Hu_2024_DigitalTwin | Personalized Heart Disease Detection via ECG Digital Twin Generation | include | P178 | full text | Agree |
| Fang_2025_PPGFlow | PPGFlowECG: Latent Rectified Flow with Cross-Modal Encoding for PPG-Guided ECG G | include | P118 | full text | Agree |
| Cardoso_2023_Bayesian | Bayesian ECG reconstruction using denoising diffusion generative models | include | P023 | full text | Agree |
| Kong_2024_fGAN | f-GAN: A frequency-domain-constrained generative adversarial network for PPG to  | include | P076 | full text | Agree |
| Jang_2025_CoFE | CoFE: A Framework Generating Counterfactual ECG for Explainable Cardiac AI-Diagn | include | P181 | full text | **Missed by me** (keyword pre-filter false negative). Added; its evaluation is thin (feature shifts only). |
| Li_2025_CLEPGAN | CLEP-GAN: An Innovative Approach to Subject-Independent ECG Reconstruction from  | include | P034 | full text | Agree |
| Xu_2025_DFNet | Lightweight Multi-task CNN for ECG Diagnosis with GRU-Diffusion | include | P100 | full text | Agree |
| Zanchi_2026_Validation | Introducing a Comprehensive Framework for Synthetic ECG Validation | include | P094 | full text | Agree |
| Russo_2026_Robustness | Assessing the robustness of evaluation metrics for synthetic ECG signal quality | await full text | P020 | not downloaded | Agree |
| Lai_2025_DiffuSETS | DiffuSETS: 12-Lead ECG generation conditioned on clinical text reports and patie | include | P049 | full text | Agree |
| Adib_2025_GANComparison | Synthetic ECG signal generation using generative neural networks | include | P140 | full text | Agree |
| Zhou_2024_BiLSTMCBAM | ECG data enhancement method using generate adversarial networks based on Bi-LSTM | await full text | P055 | not downloaded | Agree |
| Nishikimi_2024_FEMVAE | Variational autoencoder-based neural electrocardiogram synthesis trained by FEM- | include | P151 | full text | Same paper; codex lists 2024, published 2023-12-22 (my year is correct). |
| Yang_2024_CECGGAN | Data imbalance in cardiac health diagnostics using CECG-GAN | include | P041 | full text | Agree |
| Kranz_2025_ECGEN | Exploring latent diffusion models for ECG generation on the minute scale | await full text | P074 | not downloaded | Agree |
| Qiu_2026_PhysDiff | A Physics-Aware Diffusion Framework for Robust ECG Synthesis Using Mesoscopic La | include | P007 | full text | Agree |
| Ji_2026_P2Es | P2Es: Physiology-Conditioned Diffusion for 12-Lead ECG Generation from PPG | include | P180 | full text | **Missed by me** (keyword pre-filter false negative). Added. |
| Zanchi_2025_Brugada | Synthetic electrocardiograms for Brugada syndrome: from data generation to exper | include | P143 | full text | Agree |
| Tiwari_2026_Minority | Minority class-aware multiclass arrhythmia detection using conditional GAN augme | include | P103 | full text | Agree |
| Zhang_2026_QualityGAN | Single-Lead ECG Arrhythmia Classification Based on Peak-Enhanced Attention Netwo | include | P131 | full text | Agree |
| Hegde_2025_Utility | ECG Synthesis and Utility Analysis - A Diffusion Model Based Approach | await full text | P060 | not downloaded | Agree |
| Xiao_2026_Disentangled | Disentangled conditional generation of ECG signals with interpretable latent fac | await full text | P051 | not downloaded | Agree |
| Dissanayake_2026_MultiStep | Continuous multi-step ECG and PPG generation through latent disentanglement | await full text | P161 | not downloaded | Agree |
| Lin_2025_TransDiff | TransDiffECG: Semantically controllable ECG synthesis via transformer-based diff | await full text | P146 | not downloaded | Agree |
| Zhang_2026_MorphDiff | MorphDiff-ECG: A Diffusion Model for Multimodal Feature Fusion of ECG Signals | await full text | P105 | not downloaded | Agree |
| Tang_2025_PCCGAN | Principal component conditional generative adversarial networks for imbalanced E | exclude | P119 | full text | **Codex exclusion is wrong**: generated waveforms are evaluated (NPRD/NRMSE/NMAE, Wasserstein, JS, KS). Kept. |
| Xiao_2025_VariableBeta | ECG Signal Generation Using Variable β-Conditional Variational Autoencoder | await full text | P059 | not downloaded | Agree |
| Xiao_2025_DisentangleAE | ECG signal generation using feature disentanglement auto-encoder | await full text | P058 | not downloaded | Agree |
| Sepahvand_2026_TransferGAN | Morphology-preserving transfer-guided GAN with adaptive discriminative loss for  | await full text | P106 | not downloaded | Agree |
| Battiston_2025_InvertibleGAN | Invertible Conditional Generative Adversarial Networks to Effectively Generate M | await full text | P095 | not downloaded | Agree |
| Simone_2025_SSLGAN | ECG synthesis for cardiac arrhythmias: Integrating self-supervised learning and  | await full text | P061 | not downloaded | Agree |
| Chen_2025_ClassifierDiff | Classifier-Guided Diffusion Model for Generating Disease-Specific ECG Data: A Ca | await full text | P033 | not downloaded | Agree |
| Wang_2025_Attacks | Presentation Attacks on the PCA-Based Biometric System Using cGAN-Generated ECGs | await full text | P183 | not downloaded | **Missed by me** (not retrieved). Added; not open access. |
| Guan_2026_WearECG | Reconstructing 12-lead ECG from 3-lead ECG using variational autoencoder to impr | include | P123 | full text | Same paper; codex cites the 2026 PLOS Digital Health version, I cite the 2025 arXiv preprint. |
| Fang_2025_CardioPPG | AI modeling photoplethysmography to electrocardiography useful for predicting ca | include | P015 | full text | Agree |
| Sang_2025_Personalization | Deep conditional generative model for personalization of 12-lead electrocardiogr | include | P042 | full text | Agree |
| Neifar_2024_DiffECG | DiffECG: A Versatile Probabilistic Diffusion Model for ECG Signals Synthesis | include | P047 | full text | Agree |
| Li_2026_EvaluationThesis | A Comprehensive Evaluation Framework for Synthetic ECG: Assessing Fidelity, Util | include | P179 | full text | Codex had the PDF; copied and extracted. Author is Yixin Li. |
| Russo_2025_HumanFeedback | Towards High-Fidelity ECG Generation: Evaluation via Quality Metrics and Human F | include | P145 | full text | Codex PDF is the Dec 2024 MSc thesis that the conference paper is based on, not the paper itself. Copied and used for extraction, labelled as such. |
| Zhou_2025_DiffECGClassification | DiffECG: Diffusion Model-Powered Label-Efficient and Personalized Arrhythmia Dia | exclude | P048 | excluded | **Codex is right**: no synthetic ECGs are generated or evaluated. **Now excluded** from my review. |
