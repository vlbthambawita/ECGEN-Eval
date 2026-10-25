# Introducing a Comprehensive Framework for Synthetic ECG Validation

**Citation:** Zanchi B and Monachino G and Metaldi M and Conte G and Meystre S and Faraci FD. *Introducing a Comprehensive Framework for Synthetic ECG Validation*. IEEE open journal of engineering in medicine and biology, 2026. DOI: 10.1109/ojemb.2026.3716291. arXiv: not applicable; first public: 2026-07-23; peer-reviewed date: 2026-07-23.

**Source/version:** [fulltext.xml](../papers/2026/Zanchi_2026_Validation/fulltext.xml). [Landing page](https://doi.org/10.1109/ojemb.2026.3716291).


**Task and model:** Pulse2Pulse-style WGAN-GP generation of Brugada typeI ECG; six-level U-Net generator, convolutional critic (§II.C).

**Data and split:** 21 patients,95.2%male,53±14y; 15s–5min16-lead acquisitions at1kHz,100Hz Chebyshev lowpass/50Hz notch, downsample500Hz;10s windows50%overlap yield1,122 ECGs. Generate1,122 eight-lead records expanded to12; no independent held-out patient evaluation (§II.A–C).

**Evaluation metrics:** Visual median-beat/IQR overlays; RR,PR,QRS,QTc and P/QRS/T axes; Mann–Whitney tests with real features aggregated per patient. ED, maximum absolute error (paper's MAE, NOT mean), cosine distance, MSE,RMSE,NMSE,RMSPE, kernel MMD,KL,DTW; FID listed but explicitly NOT used. Real–fake median distances contextualized by real intra-/interpatient distances (§II.D–E,TableII). Metric equations in supplement, not main text. Expert accuracy,sensitivity,specificity,PPV,NPV,F1 (TableIII).

**Training objectives:** WGAN-GP named; paper calls it gradient clipping, although GP and clipping differ. Weight not given in main text; original hyperparameters inherited. Adam1e−4,batch32,2000epochs (§II.C). No loss ablation.

**Reported evidence:** Morphology p>.05 across7 features is non-rejection, not demonstrated equivalence. Expert accuracy50.6%, sensitivity62.3%,specificity39%,F1=55.04% (TablesII–III). n_real=21 patient medians vs n_synthetic=1122; dependence among synthetic records from same trained generator is unaccounted for.

**Clinical utility, experts and privacy:** One cardiologist >5y experience,2244 balanced real/synthetic cases, blinded to prevalence (§II.E). No downstream classifier experiment; independent Brugada data proposed as future work. Linked seven-reader report Zanchi_2025_Brugada is not an independent cohort. Pairwise-distance checks are not membership inference.

**Reproducibility:** Framework and supplementary appendix are described; training and synthetic resources claimed, not executed. Dataset size and sample units distinguish21 people from1122 overlapping windows.

**Critical assessment:** Reviewer assessment: strong practical use of real–real reference distances and patient aggregation. Failure to reject a difference cannot establish equivalence or no memorization; held-out patients and explicit equivalence bounds are needed.
