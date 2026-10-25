# PPGFlowECG: Latent Rectified Flow with Cross-Modal Encoding for PPG-Guided ECG Generation and Cardiovascular Disease Detection

**Citation:** Xiaocheng Fang and Jiarui Jin and Haoyu Wang and Che Liu and Jieyi Cai and Yujie Xiao and Guangkun Nie and Bo Liu and Shun Huang and Hongyan Li and Shenda Hong. *PPGFlowECG: Latent Rectified Flow with Cross-Modal Encoding for PPG-Guided ECG Generation and Cardiovascular Disease Detection*. arXiv, 2025. DOI: not identified. arXiv: 2509.19774v3; first public: 2025-09-24; peer-reviewed date: not verified.

**Source/version:** [paper.pdf](../papers/2025/Fang_2025_PPGFlow/paper.pdf); [landing.html](../papers/2025/Fang_2025_PPGFlow/landing.html). [Landing page](https://arxiv.org/abs/2509.19774v3).


**Task and model:** PPGFlowECG: shared variational CardioAlign representation followed by PPG-conditioned latent rectified flow; paired waveform subgroup (pp.3–5).

**Data and split:** Lead II, 10-s non-overlapping windows, 128 Hz, z-score. MC-MED official split: 10,356,840/1,299,869/37,052 train/validation/test windows; MIMIC-AFib 35 subjects, 2044/577 train/test; VitalDB 6388 patients, 1,007,165/10,720; BIDMC53, 1458/326. Other datasets split 80/20 by subject (TableII, p.5).

**Evaluation metrics:** Paired MAE/RMSE ↓ normalized amplitude and Hamilton-derived HR-MAE ↓ bpm. Per-class/macro AUROC, AF accuracy/F1 ↑. Five cardiologists: real/fake accuracy against chance with 95% CI, and AF accuracy/sensitivity/specificity mean±SD across raters. Grad-CAM and waveform overlays qualitative; no FID or explicit privacy metric in analyzed version (pp.5–8).

**Training objectives:** CardioAlign Eq.6 = global mean plus symmetric Gaussian-KL alignment (Eq.3) + bidirectional contrastive instance loss (Eq.4, temperature not numerically specified) + cross-modal decoding MSE (Eq.5), unit weights. Stage2 squared velocity flow matching E||v−(target−noise)||² Eq.8; frozen encoder/decoder at generation stage; Euler solver (pp.3–4).

**Reported evidence:** Module ablations TableV HR-MAE 3.28 baseline, 1.93 alignment, 2.12 flow, 1.80 full; macro AUROC53.1/61.5/58.9/63.1%. Main10 steps;5 steps slightly better in Fig.5. No isolated ablation for each alignment loss or training-seed intervals (pp.6–7).

**Clinical utility, experts and privacy:** Zero-shot MC-MED→MIMIC-AFib AF F1 .82 versus internal .87. Five board-certified cardiologists (1 junior,3 mid,1 senior), randomized50real/50synthetic real/fake task; one rater accuracy .65. Separate100 balanced AF cases under PPG, PPG+realECG, PPG+syntheticECG: accuracy .81±.13/.89±.07/.87±.09 (p.8 TableVI). No MIA.

**Reproducibility:** Dataset split counts and expert composition unusually explicit; no released-code verification. Blinding across repeated modality conditions, washout, rater agreement and detailed signal-quality exclusion implementation not established.

**Critical assessment:** Expert clinical task is more informative than real/fake discrimination alone, but small sample and repeated cases limit inference. Multiple trained-dataset results are not all external validation; only the stated zero-shot experiment is. Lower MAE does not consistently coincide with best HR error across baselines.
