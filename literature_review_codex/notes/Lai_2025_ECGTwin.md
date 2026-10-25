# ECGTwin: Personalized ECG Generation Using Controllable Diffusion Model

**Citation:** Yongfan Lai and Bo Liu and Xinyan Guan and Qinghao Zhao and Hongyan Li and Shenda Hong. *ECGTwin: Personalized ECG Generation Using Controllable Diffusion Model*. arXiv, 2025. DOI: not identified. arXiv: 2508.02720v2; first public: 2025-08-01; peer-reviewed date: not verified.

**Source/version:** [paper.pdf](../papers/2025/Lai_2025_ECGTwin/paper.pdf); [landing.html](../papers/2025/Lai_2025_ECGTwin/landing.html). [Landing page](https://arxiv.org/abs/2508.02720v2).


**Task and model:** Personalized reference-ECG+target-text/demographics latent diffusion;contrastive Individual Base Extractor and AdaX condition injection (§3).

**Data and split:** MIMIC794,372 retained records split744,372/50,000 then grouped by subject into6,408,782/399,499 pairs;explicit cross-split patient exclusion unclear in AppendixC. 12leads10s102.4Hz. ExternalPTB-XL4,269pairs,no fine-tuning (AppendicesC–D).

**Evaluation metrics:** Inherited Net1D-based FID/manifoldprecision,recall,F1,HRMAE,CLIP;intra-minus-interpatient cosine similarity Eq9,silhouette,t-SNE;personalized diagnosis metrics and inference steps/s. Quality tests5repeats mean±SD (Table1,AppendixD). Same extractor trains and evaluates identity consistency.

**Training objectives:** Stage1 symmetric contrastive cosine loss with learnabletemperature,positive same-patient pairs (Eq1; denominator printed j≠i);stage2 DDPMnoiseMSE (Eq8). Frozen pretrainedDiffuSETSVAE;no new reconstructionloss. Reference condition and base-vector dropout.15;batch65536 via accumulation for extractor (AppendixC).

**Reported evidence:** Table1 DiT FID26±2.8,F1 .884±.002,HRMAE7.03±.50. External HRMAE10.23 worse than two ablations6.88/7.35 despite bestFID41;tradeoff matters (Table6). Component ablations isolate conditioning architecture,not denoising objective.

**Clinical utility, experts and privacy:** 293held-out evaluation patients;earliestECG reference,synthetic normal/abnormal twins fine-tune patient classifiers,remainingtest records train population model (§4.4). No empirical privacy test; preserving identity raises distinct disclosure questions.

**Reproducibility:** https://github.com/Raiiyf/ECGTwin;not inspected. Preprint analyzed;CIKM2026 program lists acceptance,publication date not independently established.

**Critical assessment:** Reviewer: personalize evaluation with an independent identity model and verify generator/VAE patient overlap;pair counts are not independent patient counts.
