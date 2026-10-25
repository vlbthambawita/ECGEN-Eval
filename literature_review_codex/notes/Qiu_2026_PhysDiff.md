# A Physics-Aware Diffusion Framework for Robust ECG Synthesis Using Mesoscopic Lattice Boltzmann Constraints

**Citation:** Qiu X and Cao H and Yang L and Wang H. *A Physics-Aware Diffusion Framework for Robust ECG Synthesis Using Mesoscopic Lattice Boltzmann Constraints*. Biology, 2026. DOI: 10.3390/biology15050431. arXiv: not applicable; first public: 2026-03-05; peer-reviewed date: 2026-03-05.

**Source/version:** [fulltext.xml](../papers/2026/Qiu_2026_PhysDiff/fulltext.xml). [Landing page](https://doi.org/10.3390/biology15050431).


**Task and model:** PhysDiff-LBM diffusion reconstructs ECG from paired PPG using lattice-Boltzmann-inspired latent physics and QRS topology mask; included as generated-waveform translation subgroup.

**Data and split:** MIMIC-III curated5000+ subjects and external VitalDB; PPG→ECG reconstruction; 128Hz, nonoverlap4s, min-max[-1,1], NeuroKit2/Pan-Tompkins (full text §§3.1–3.2). Exact split sizes and subject disjointness unclear.

**Evaluation metrics:** Paired RMSE, Pan-Tompkins HR-MAE, raw-signal vector Fréchet distance; downstream AF/arrhythmia diagnostic metrics, t-SNE (evaluation §§3.2,3.5). Distribution FD treats flattened raw windows, not learned ECG features.

**Training objectives:** Total lambda_diff noise-prediction MSE + lambda_reg QRS-mask BCE + lambda_phys squared temporal derivative versus LBM momentum field (Eqs.17–19); weights not specified. Preprocess uses128Hz/4s windows and 32-sample QRS mask (Eq.21).

**Reported evidence:** Ablation table: full MIMIC RMSE .22, HRMAE1.26, FD6.23; VitalDB .25,1.95,4.35. No CIs/seeds in displayed table.

**Clinical utility, experts and privacy:** Paper claims downstream validity; independent classifier split and training/testing provenance require scrutiny. No clinicians or privacy attacks.

**Reproducibility:** Full XML read; paper has equations/ablation, but high-level architecture and derived “clinical-grade” wording should not substitute for patient-level external validation.

**Critical assessment:** Task is PPG-conditioned reconstruction, not free unconditional generation. Physical residual is against a fitted simplified model; agreement can reflect model assumptions.
