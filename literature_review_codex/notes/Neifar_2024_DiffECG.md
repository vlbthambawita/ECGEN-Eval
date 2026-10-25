# DiffECG: A Versatile Probabilistic Diffusion Model for ECG Signals Synthesis

**Citation:** Nour Neifar and Achraf Ben-Hamadou and Afef Mdhaffar and Mohamed Jmaiel. *DiffECG: A Versatile Probabilistic Diffusion Model for ECG Signals Synthesis*. IEEE SERA 2024, 2024. DOI: not identified. arXiv: 2306.01875; first public: 2023-06-02; peer-reviewed date: not verified.

**Source/version:** [paper.pdf](../papers/2024/Neifar_2024_DiffECG/paper.pdf); [landing.html](../papers/2024/Neifar_2024_DiffECG/landing.html). [Landing page](https://arxiv.org/abs/2306.01875).


**Task and model:** Conditional DDPM with a task-aware U-Net for heartbeat generation, partial-signal imputation and forecasting; SERA 2024 publication qualifies although arXiv first report in 2023 is outside window.

**Data and split:** MIT-BIH 48 records/two leads, 360Hz; MLII; annotated N,V,F beats of 270 samples around R peak; random 70/30 signal-wise split, not patient grouped (pp.3–4).

**Evaluation metrics:** Generation RMSE/MAE, FID, DTW, EMD, MMD per class (Table II); downstream classifier accuracy/precision/recall/F1 after synthetic augmentation (Table I). Feature extractor details for FID are incomplete (pp.4–5).

**Training objectives:** Conditional DDPM noise-prediction MSE Eq.3. Generation task masks all waveform values and conditions on class/task embeddings. Additional waveform MSE Eq.4 applies to imputation/forecasting, not unconditional generation (p.3).

**Reported evidence:** Table II normal class: RMSE1.68e-3, DTW22.10, FID1.29e-2, EMD1.54e-2, MMD.40. One classifier F1 rises .77→.96 with synthetic augmentation (Table I). Other class metrics are mixed versus strongest GAN baselines.

**Clinical utility, experts and privacy:** Three classifier baselines evaluated with real-only and synthetic augmentation. No experts/privacy attack. Signal-wise split risks patient leakage; no external data.

**Reproducibility:** Full arXiv PDF;1000 diffusion steps, beta .0001–.02, Adam .001. No run intervals. IEEE SERA DOI10.1109/SERA61261.2024.10685651, conference date 2024-05-30.

**Critical assessment:** Unified task-aware architecture is useful, but metric implementation is incomplete and record-level splitting may inflate evaluation. Restrict conclusions to reported protocol.
