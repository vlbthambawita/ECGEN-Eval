# Synthetic ECG Generation for Data Augmentation and Transfer Learning in Arrhythmia Classification

**Citation:** José Fernando Núñez and Jamie Arjona and Javier Béjar. *Synthetic ECG Generation for Data Augmentation and Transfer Learning in Arrhythmia Classification*. arXiv, 2024. DOI: not identified. arXiv: 2411.18456v1; first public: 2024-11-27; peer-reviewed date: not verified.

**Source/version:** [paper.pdf](../papers/2024/Nunez_2024_Augmentation/paper.pdf); [landing.html](../papers/2024/Nunez_2024_Augmentation/landing.html). [Landing page](https://arxiv.org/abs/2411.18456v1).


**Task and model:** Comparison of SSSD/Diffwave,conditionalUnet1D(Time-Diffusion),and Time-VQVAE with bidirectional masked-tokenpriors (§5).

**Data and split:** PTB-XL andChapman,12lead10s,seven commonrhythm classes. Dataset descriptive counts18,885 and45,152patients;per-class selectedcountsTable4. Hz/split patientgrouping not fully resolved from methods;do not infer from originaldataset (§4,§8).

**Evaluation metrics:** t-SNE,UMAP,PaCMAP;RBF-MMD;two-sample real/fakeclassifier accuracy50%target;classificationaccuracy,precision,recall,F1,ROC-AUC;25repeataverages (§7–8).

**Training objectives:** Diffusion variational/noisedenoising objectives inherited;Time-VQVAE separatesLF/HF STFT quantization thenmasked-tokenpriortraining. Complete weightedobjectives/codeconfigs not specified in paper (§5);classificationloss separate from generatorloss.

**Reported evidence:** Single-datasetaugmentation benefit limited;mergingdatasets improves results;syntheticpretraining alone remains weaker thanreal-only (Results,Conclusion).25repeats improve repeatability but do not fix patientleakage.

**Clinical utility, experts and privacy:** TRTR,TSTS,TSTR,TRTS,mixedtrain/realtest;fine-tunes classifierhead on20/40/60/80%realdata withfeaturelayersfrozen (§7–8). No expert/privacyattackstudy.

**Reproducibility:** Selects openimplementations thattrain without major tuning;reproducibility selection limits completeness of modelcomparison. Preprint analyzed.

**Critical assessment:** Reviewer: negativefindings and real-only reference are valuable;TSTS and embeddings cannot replace held-outrealutility.
