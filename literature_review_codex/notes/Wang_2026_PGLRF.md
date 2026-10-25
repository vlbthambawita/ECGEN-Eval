# PG-LRF: Physiology-Guided Latent Rectified Flow for Electro-Hemodynamic PPG-to-ECG Generation

**Citation:** Xiaoda Wang and Minxiao Wang and Kaiqiao Han and Defu Cao and Ching Chang and Yidan Shi and Runze Yan and Xiao Luo and Yan Liu and Xiao Hu and Yizhou Sun and Wei Wang and Carl Yang. *PG-LRF: Physiology-Guided Latent Rectified Flow for Electro-Hemodynamic PPG-to-ECG Generation*. arXiv, 2026. DOI: not identified. arXiv: 2605.12541v1; first public: 2026-05-09; peer-reviewed date: not verified.

**Source/version:** [paper.pdf](../papers/2026/Wang_2026_PGLRF/paper.pdf); [landing.html](../papers/2026/Wang_2026_PGLRF/landing.html). [Landing page](https://arxiv.org/abs/2605.12541v1).


**Task and model:** PPG-conditioned latent rectified flow with physiology-aware variational autoencoder and fitted electro-hemodynamic simulator; paired waveform generation subgroup (pp.4–7).

**Data and split:** MC-MED source: 118,385 visits, 70,545 adults. Synchronized 10-s, one-channel ECG at 120 Hz and PPG at 40 Hz; per-window z-score, invalid windows excluded; official train/test splits used. Actual retained window counts and patient separation details not restated (p.7).

**Evaluation metrics:** Paired MAE/RMSE ↓ (normalized units), FD/FID ↓ (distinct names, implementation/extractor insufficiently specified), HR-MAE ↓ bpm; three-run mean±SD. Paired fiducial MAE: PR, QRS, QT, QTcF, P/T duration in ms and ST-J60 in normalized amplitude. Visit-level ICD per-class/macro AUROC ↑; classifier architecture and split held constant (pp.7–9 Tables1–3).

**Training objectives:** PAE Eq.19: lambda_PAT circular phase-delay squared error + dual waveform reconstruction + beta KL to N(0,I) + lambda_GPA mean/symmetric-posterior-KL alignment + lambda_LID bidirectional contrastive loss + lambda_CSD cross-decoding MSE. Flow Eq.26: velocity MSE + lambda_e ECG Euler residual + lambda_p PPG Euler residual; residuals act on differentiably integrated terminal generated waveform, frozen decoder and forward mapper (Eqs.21–26). Main training coefficients/contrastive temperature not reported numerically in inspected methods. Separate simulator-fitting objective Eq.36 uses ECG 5, PPG .25, derivative 3, peak-window 12; first half ECG-only warmup; top-100 training ICD groups (Appendix B pp.14–15).

**Reported evidence:** Removing simulator guidance worsens HR-MAE 3.94±.76 to 4.94±.57 and FID 37.79±.27 to 45.90±.27; separate-autoencoder ablation HR 6.36±.07. Three runs; no uncertainty for external cohorts (Table1).

**Clinical utility, experts and privacy:** Macro-AUROC .633±.01 versus PPG .545±.04. Authors explicitly caution that visit ICD labels are not ECG-only diagnoses (pp.8–9). No blinded experts, privacy attacks, or external dataset experiment reported.

**Reproducibility:** Preprint; equations and simulator-fitting weights available. Main loss weights, exact metric feature model, retained counts and fiducial failure policy remain insufficient for independent reproduction.

**Critical assessment:** Physiology guidance improves measured endpoints within this experiment; it does not establish uniquely recoverable electrical information from PPG. Simulator consistency means proximity to a fitted model, not clinical correctness. Unlike an input-only regularizer, terminal-sample losses here specify a gradient path.
