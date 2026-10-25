# Synthetic ECG signal generation using generative neural networks

**Citation:** Adib E and Afghah F and Prevost JJ. *Synthetic ECG signal generation using generative neural networks*. PloS one, 2025. DOI: 10.1371/journal.pone.0271270. arXiv: not applicable; first public: 2025-03-25; peer-reviewed date: 2025-03-25.

**Source/version:** [fulltext.xml](../papers/2025/Adib_2025_GANComparison/fulltext.xml). [Landing page](https://doi.org/10.1371/journal.pone.0271270).


**Task and model:** Five normal-beat GANs: classic, DC-DC, BiLSTM-DC, AE/VAE-DC and WGAN (Model designs).

**Data and split:** MIT-BIH48 records/47people,360Hz;109,338 segmented beats,90,502 normal;280points resampled256. Generator uses normal beats. Patient-disjoint holdout not established (Dataset and segmentation).

**Evaluation metrics:** DTW, curve Fréchet and Euclidean distances, evaluated as all-pairs300×300 means, distance to chosen template, minimum/best beat and thresholded productivity fraction; subjective morphology inspection (Methods1–5,Eqs14–22). Template/threshold choice changes rankings. Classification accuracy,precision,recall,F1/confusion matrices (Tables13–16). No FID: curve Fréchet is different.

**Training objectives:** Hyperparameter subsection states BCE for models,30epochs,batch9; hybrid model adversarial plus weightedL1 reconstruction, coefficient not reported. WGAN naming and blanket BCE statement leave objective ambiguity; do not substitute a presumed Wasserstein implementation.

**Reported evidence:** Productivity72.3% for classicGAN under DTW, whereas expert visual judgment favors BiLSTM/WGAN (Table12,Performance metrics). Artificially imbalanced binary classifier accuracy .54→.97 after augmentation; real-balanced .95 (Tables13–16). No repeated-seed interval; inconsistent test supports across tables.

**Clinical utility, experts and privacy:** Binary normal/LBBB stress test: normal training class reduced to500 versus~6460 LBBB, then restored using synthetic beats;3216 nominal unseen test beats. No documented patient exclusion from generator pool. Expert protocol unspecified; no privacy attack.

**Reproducibility:** Published2025 article analyzed; code/data statements in original. Exact template choice, hybrid weight and test membership require clarification.

**Critical assessment:** Reviewer: minimum-distance scores reward best-case selection and larger sample pools; productivity threshold constructed from generated outputs is not independent clinical acceptance.
