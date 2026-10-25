# SSSD-ECG-nle: New Label Embeddings with Structured State-Space Models for ECG generation

**Citation:** Sergey Skorik and Aram Avetisyan. *SSSD-ECG-nle: New Label Embeddings with Structured State-Space Models for ECG generation*. arXiv, 2024. DOI: not identified. arXiv: 2407.11108v1; first public: 2024-07-15; peer-reviewed date: not verified.

**Source/version:** [paper.pdf](../papers/2024/Skorik_2024_SSSDnle/paper.pdf); [landing.html](../papers/2024/Skorik_2024_SSSDnle/landing.html). [Landing page](https://arxiv.org/abs/2407.11108v1).


**Task and model:** Conditional SSSD diffusion with separate present/absent label embeddings and a 1×1 folding convolution (§IV.B–C).

**Data and split:** PTB-XL 21,837, 10 s, 100 Hz, eight independent leads expanded to 12; retains amplitude, reports bandpass preprocessing. Folds1–8 train,9 validation,10 test; patient grouping follows dataset folds but not independently audited (§IV.A,E).

**Evaluation metrics:** TSTR/TRTS G-mean sqrt(sensitivity×specificity), F1, multilabel ROC-AUC; expert diagnostic accuracy and real/fake confusion matrix; convergence versus processed samples. Relation metrics and TSTS explicitly rejected as uninformative (§IV.D–V). Distinguish classification F1 from manifold F1.

**Training objectives:** Inherited diffusion denoising/noise objective described in diffusion background (§III); no new loss term. SSSD settings inherited; exact ECG-specific weighting not separately supplied. New contribution is conditioning, not a changed training loss.

**Reported evidence:** TableI PVC TSTR F1 0.338→0.561; AFIB F1 0.720→0.709 despite broader improvement language. TableII multilabel TSTR AUROC0.820, TRTS0.894. TableIII includes duplicated-positive baseline. Checkpoint study shows disease-dependent convergence and possible undertraining (TableIV).

**Clinical utility, experts and privacy:** 200 ECGs (100 real/100 synthetic) for diagnostic reporting; 20 each of five categories. Separate 380-example detection test: 100 real/280 synthetic; confusion matrix 99,1,1,279 means 378/380 correct (99.47%). Text inconsistently calls 280 records additional to 100 synthetic; table denominator retained. Third physician for detection; years of experience/blinding details not reported (§V.B, TablesV–VI). No privacy attack.

**Reproducibility:** Reports difficulty reproducing original SSSD multilabel TSTR. Generated data/expert results promised; no code inspection. Seed uncertainty not reported.

**Critical assessment:** Reviewer assessment: unusually direct evidence that reasonable downstream utility can coexist with obvious synthetic appearance. Real/fake detectability is not a privacy metric, despite the authors' privacy framing.
