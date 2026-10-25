# Synthetic electrocardiograms for Brugada syndrome: from data generation to expert cardiologists evaluation

**Citation:** Zanchi B and Monachino G and Faraci FD and Metaldi M and Brugada P and Sarquella-Brugada G and Behr ER and Brugada J and Crotti L and Belhassen B and Conte G. *Synthetic electrocardiograms for Brugada syndrome: from data generation to expert cardiologists evaluation*. European heart journal. Digital health, 2025. DOI: 10.1093/ehjdh/ztaf039. arXiv: not applicable; first public: 2025-04-24; peer-reviewed date: 2025-04-24.

**Source/version:** [fulltext.xml](../papers/2025/Zanchi_2025_Brugada/fulltext.xml). [Landing page](https://doi.org/10.1093/ehjdh/ztaf039).


**Task and model:** Pulse2Pulse GAN generates 12-lead Brugada-pattern ECGs and expert panel tests real/fake distinguishability (Methods/results).

**Data and split:** 21 Brugada patients; 5-min 1kHz 12-lead real records, synthetic matched format; 1,122 generated segments? The evaluated set comprises 2244 ECG instances, half/half; same patient cohort as 2026 Zanchi validation.

**Evaluation metrics:** Real/fake accuracy, sensitivity, specificity, F1; Cohen kappa within-rater between rounds; Wilcoxon round comparison (Statistical analysis section).

**Training objectives:** GAN Pulse2Pulse details and objective delegated to prior paper, no coefficients/architecture/training split in article.

**Reported evidence:** 7 Brugada specialists (>15y), blind, randomized2244 balanced traces, repeated after ≥2h. Accuracy40% then42%; sensitivity58%, specificity22→26%; kappa−.12 to.80 (Methods/results).

**Clinical utility, experts and privacy:** Strong expert-design detail, but same21-patient source and synthetic set as Zanchi2026; not independent replication. No held-out clinical outcome or privacy test.

**Reproducibility:** Published full XML read; data governance/consent noted. Model full methods not reported, cite predecessor separately if needed.

**Critical assessment:** Chance-level distinction supports perceptual similarity only, not clinical interchangeability; low specificity shows inconsistent labeling.
