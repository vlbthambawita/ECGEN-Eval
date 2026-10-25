# Single-Lead ECG Arrhythmia Classification Based on Peak-Enhanced Attention Network and Quality-Aware GAN Data Augmentation Framework

**Citation:** Zhang Y and Xia Y. *Single-Lead ECG Arrhythmia Classification Based on Peak-Enhanced Attention Network and Quality-Aware GAN Data Augmentation Framework*. Sensors (Basel, Switzerland), 2026. DOI: 10.3390/s26123852. arXiv: not applicable; first public: 2026-06-17; peer-reviewed date: 2026-06-17.

**Source/version:** [fulltext.xml](../papers/2026/Zhang_2026_QualityGAN/fulltext.xml). [Landing page](https://doi.org/10.3390/s26123852).


**Task and model:** Quality-aware GAN augmentation learns soft labels from ECG quality/rhythm signals, generates 12-lead records, evaluates classifier and waveform quality.

**Data and split:** PhysioNet2017-derived 8,528 records, remove46 poor quality, 80/20 record split then 10-s windows; no patient-level separation specified. AF examples expanded1841→6000.

**Evaluation metrics:** Classifier accuracy/F1, Kurtosis excess K=E4/var², ECG quality diagnostics; classifier parameter/FLOPs and inference latency refer downstream classifier rather than GAN (Methods/Table10–11).

**Training objectives:** Soft quality targets alpha=.7; generator/discriminator adversarial objective (Eq.10); positive-label loss is −E[y logD] only, not full soft-label BCE. Eq.11 specificity denominator malformed (includes TN twice).

**Reported evidence:** GAN ablation F1 .816 vs noaug .793; full system .880 includes classifier architecture changes, not attributable solely to waveform fidelity (Table10–11).

**Clinical utility, experts and privacy:** Augmentation classification benefit only; no blinded reviewers or privacy attacks.

**Reproducibility:** Full XML; detailed data and architecture but no patient-stratification protocol or independent test/seed CIs.

**Critical assessment:** High kurtosis may also signal sharp artifacts, so quality weighting requires clinical labels and robustness controls; classifier and generator changes are confounded.
