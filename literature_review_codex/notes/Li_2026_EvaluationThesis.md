# A Comprehensive Evaluation Framework for Synthetic ECG: Assessing Fidelity, Utility, and Privacy

**Citation:** Yixin Li. *A Comprehensive Evaluation Framework for Synthetic ECG: Assessing Fidelity, Utility, and Privacy*. University of Waterloo MSc thesis, 2026. DOI: not identified. arXiv: not applicable; first public: 2026-05-08; peer-reviewed date: not verified.

**Source/version:** [paper.pdf](../papers/2026/Li_2026_EvaluationThesis/paper.pdf). [Landing page](https://uwspace.uwaterloo.ca/items/0fff9cd3-cb39-4e3a-b81d-2ade38b1dd22).


**Task and model:** University of Waterloo MSc thesis evaluates conditional SSSD-ECG on PTB-XL using multi-domain fidelity, TSTR/TRTR utility, forecasting, and seven membership attacks (repository first deposit 2026-05-08; thesis §§3–4).

**Data and split:** PTB-XL 21,837 records/18,885 patients,12 leads,10s, downsampled 100Hz/1000 samples, per-lead dataset z-score. Official folds1–8 train,9 validation,10 test, multi-hot five superclass labels; diffusion uses 8 independent leads and derives 4 (pp.42–48).

**Evaluation metrics:** Utility: ResNet AUROC/F1,1000 bootstrap CIs; lead-aware one-step LSTM RMSE/Pearson. Fidelity: 12-lead ACF MAE, Welch Hann PSD log-MAE, lead-specific FastDTW 20-random-candidate minimum with real-real ratio, db4 level4 normalized wavelet energy MAE, NeuroKit2 LeadII HR/RR/SDNN/RMSSD/QRS count/R amplitude MAPE (pp.49–53). Privacy: seven black/grey-box attacks in Euclidean, DTW, wavelet domains; AUC, TPR@1/10%FPR, DCR/NNDR ratios, global and single-label subgroup (pp.54–58).

**Training objectives:** 200-step conditional DDPM, linear beta 1e-4 to .02; noise-prediction MSE; eight channels,36 bidirectional S4 residual layers, class embedding; Adam 2e-4,2000 epochs,H100 (pp.46–48).

**Reported evidence:** TSTR AUC .828 [.818,.839] vs TRTR .886 [.878,.895]; TSTR F1 .607/.685. ACF MAE .0065, PSD log-MAE .269, LeadI DTW RS/RR ratio1.003. Global MIA AUC .500–.539; DTW .539±.009 over five seeds. Per-class Euclidean-feature HYP AUC .607 on only56 nonmembers (pp.61,63,70,87–90). HRV discrepancies despite strong aggregate ACF/DTW (pp.86,96).

**Clinical utility, experts and privacy:** No clinicians. Global MIA is low, but subgroup HYP attack .607 has a small evaluation group. TSTR remains below real-trained performance, HYP weakest. Forecasting Pearson .918 vs .923; RMSE .1058 vs .1025 (p.63).

**Reproducibility:** Explicit implementation, splits, seeds and attack detail; thesis not peer reviewed. Validate with independent implementation and shadow attacks.

**Critical assessment:** Useful comparison of aggregate similarity with precise HRV and attacks. Single split/checkpoint and PTB-XL constrain generalization; low attack AUC does not establish formal privacy, fairness or attribute protection.
