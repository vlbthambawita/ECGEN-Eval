# CoFE: A Framework Generating Counterfactual ECG for Explainable Cardiac AI-Diagnostics

**Citation:** Jong-Hwan Jang and Junho Song and Yong-Yeon Jo. *CoFE: A Framework Generating Counterfactual ECG for Explainable Cardiac AI-Diagnostics*. arXiv, 2025. DOI: not identified. arXiv: 2508.16033v1; first public: 2025-08-22; peer-reviewed date: not verified.

**Source/version:** [paper.pdf](../papers/2025/Jang_2025_CoFE/paper.pdf); [landing.html](../papers/2025/Jang_2025_CoFE/landing.html). [Landing page](https://arxiv.org/abs/2508.16033v1).


**Task and model:** StyleGAN2 waveform counterfactual framework with learned inversion and fixed diagnostic predictor; explicitly measures generated waveform features (§§2,4).

**Data and split:** Generator300,000 MIMIC-IV12-lead ECGs at250Hz; diagnostic models use10s. Evaluation1000 MIMIC ECGs disjoint from potassium predictor training; generator/patient-level separation not established. Paper calls AF classifier training PhysioNet2017 while describing12-lead models: lead harmonization unclear (pp.2–3).

**Evaluation metrics:** Before/after P amplitude(mV), RR variability(ms; exact statistic unspecified), T amplitude(mV), QRSduration(ms); p<.05 for each without named test, multiplicity, effect uncertainty or detector details. Saliency maps and prediction changes qualitative (p.4 Table1).

**Training objectives:** Standard logistic minimax GAN objective; frozen-generator encoder reconstruction squared L2. Counterfactual latent-code optimization minimizes target-class cross-entropy through frozen predictor and generator (p.2). This is inference-time optimization, not generator retraining. Regression-target objective for potassium example not specified by the displayed class-CE equation.

**Reported evidence:** P amplitude .09→.04mV, RR variability46.17→85.44ms, T .18→.58mV, QRS95.84→121.98ms (Table1). No isolated loss ablation, synthetic utility comparison, realism coverage score or seed analysis.

**Clinical utility, experts and privacy:** No blinded clinical assessment, membership attack or downstream TSTR. Agreement with classifier-targeted features is not independent diagnosis; fixed predictor is both optimization target and displayed success measure (§§2.2,4).

**Reproducibility:** Demo video supplied; generator checkpoints, training splits, counterfactual stopping criterion and hyperparameters insufficiently specified in5-page report.

**Critical assessment:** Shows how to inspect morphology under counterfactual edits but does not demonstrate causality. Latent optimization alone does not ensure samples remain representative of the original latent prior. Report target success together with edit size and independent clinical review.
