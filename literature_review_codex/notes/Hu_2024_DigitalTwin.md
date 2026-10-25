# Personalized Heart Disease Detection via ECG Digital Twin Generation

**Citation:** Yaojun Hu and Jintai Chen and Lianting Hu and Dantong Li and Jiahuan Yan and Haochao Ying and Huiying Liang and Jian Wu. *Personalized Heart Disease Detection via ECG Digital Twin Generation*. IJCAI2024, 2024. DOI: 10.24963/ijcai.2024/649. arXiv: 2404.11171v2; first public: 2024-04-17; peer-reviewed date: not verified.

**Source/version:** [paper.pdf](../papers/2024/Hu_2024_DigitalTwin/paper.pdf); [landing.html](../papers/2024/Hu_2024_DigitalTwin/landing.html). [Landing page](https://arxiv.org/abs/2404.11171v2).


**Task and model:** LA VQ-Editor edits a patient’s normal ECG with disease features from a reference patient using vector quantization, ClinicalBERT text guidance and adversarial waveform decoding (pp.3–5).

**Data and split:** PTB-XL single-label superclasses; 291 patients with normal and disease records reserved for personalized testing. Remaining patients train/validate. R-peak crop: 100 points before first to 100 after seventh peak, resized to 4096; 12 leads. Training source rate not explicitly restated in inspected methods (p.5).

**Evaluation metrics:** ECG-feature Gaussian Fréchet ResNet Distance (FRD) ↓ and ResNet Score (IS analogue) ↑ using training-set pretrained 1D ResNet-101; manifold precision/recall/F1 ↑. Patient/record accuracy, F1, AUROC and ATE difference in group accuracy ↑. DTW to same-patient disease record ↓ for ablations. Privacy attack F1 ↑ means greater risk; feature Euclidean nearest-neighbour threshold epsilon=tau×mean distance. t-SNE qualitative (pp.5–8 Tables1–4).

**Training objectives:** Generator Eq.10: logistic softplus adversarial + L2 reconstruction (Eq.8 written as norm, not explicitly squared) + 1−cosine disease similarity + masked VQ codebook/commitment squared errors, unit coefficients. Discriminator Eq.13: softplus adversarial + disease cosine loss. VQ terms use stop gradients; frozen ClinicalBERT; cross-attention threshold .5 (pp.3–5).

**Reported evidence:** Table3 FRD 1.6286 against real-real .3014, recall .6438 versus CGAN .0688. Ablation Table4 full DTW 5.322×10^3 and ATE 5.13%; component removals worsen these. No multi-seed uncertainty reported.

**Clinical utility, experts and privacy:** For each experimental test patient’s normal ECG, 50 disease variants are added to classifier training; this is explicitly personalized/transductive utility, not ordinary unseen-patient TSTR. Real 15,553 with generated 8,600/17,200/34,400 compared. ATE can rise partly because control-group performance falls (p.6). Privacy feature-distance attack tested across thresholds, no DP guarantee; no independent experts.

**Reproducibility:** Detailed architecture, optimizer and 500-epoch generator training given. Feature extractor trained on training data. Attack calibration, seed uncertainty and complete paired-reference selection need further specification.

**Critical assessment:** Retention of target patient identity and removal of reference identity are different goals. A low single-attack F1 does not prove anonymity. Different acquisition times mean same-patient disease ECGs are not exact paired counterfactual ground truth.
