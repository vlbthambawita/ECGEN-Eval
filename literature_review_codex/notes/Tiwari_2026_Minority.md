# Minority class-aware multiclass arrhythmia detection using conditional GAN augmentation

**Citation:** Tiwari A and Kishore J and Singh R. *Minority class-aware multiclass arrhythmia detection using conditional GAN augmentation*. Scientific reports, 2026. DOI: 10.1038/s41598-026-51237-z. arXiv: not applicable; first public: 2026-05-11; peer-reviewed date: 2026-05-11.

**Source/version:** [fulltext.xml](../papers/2026/Tiwari_2026_Minority/fulltext.xml). [Landing page](https://doi.org/10.1038/s41598-026-51237-z).


**Task and model:** Class-conditional WGAN-GP generates minority PhysioNet2020 ECG classes for eight-class diagnosis augmentation (Methods §§2–4).

**Data and split:** PhysioNet2020, eight classes,360Hz single lead,360 samples. Each class360 synthetic examples; fivefold CV reported but patient partition details absent.

**Evaluation metrics:** Classifier accuracy/precision/recall/F1, DTW and SSIM waveform similarity; definitions and real/synthetic pair protocol unclear (Results tables3–4).

**Training objectives:** cWGAN-GP critic objective includes gradient penalty coefficient10; Eq.1 sign places GP under critic maximization, inconsistent with conventional minimization description. Auxiliary class loss weight unspecified. Diffusion not used.

**Reported evidence:** Noaug macro F1 .78; GAN +ResNet .89; full .94 (Table3). Table4 fivefold scores .932,.945,.938,.941,.944 incompatible with printed SD .012 under common sample SD.

**Clinical utility, experts and privacy:** Only TSTR-like classifier augmentation assessment, class balance and grouped patient split unclear; no expert or attack.

**Reproducibility:** Full XML; equations and tables have material inconsistencies; code not inspected.

**Critical assessment:** Potential record-level leakage with 360Hz chopped segments. DTW/SSIM do not establish diagnostic validity; Table variance is internally inconsistent.
