# Generating Realistic Multi-Beat ECG Signals

**Citation:** Paul Pöhl and Viktor Schlegel and Hao Li and Anil Bharath. *Generating Realistic Multi-Beat ECG Signals*. arXiv, 2025. DOI: not identified. arXiv: 2505.18189v1; first public: 2025-05-19; peer-reviewed date: not verified.

**Source/version:** [paper.pdf](../papers/2025/Pohl_2025_MultiBeat/paper.pdf); [landing.html](../papers/2025/Pohl_2025_MultiBeat/landing.html). [Landing page](https://arxiv.org/abs/2505.18189v1).


**Task and model:** Hierarchical single-beat diffusion, learned multivariate feature trajectory, then feature-matched concatenation for multiminute ECG (§III).

**Data and split:** MIT-BIH Supraventricular:87h/47subjects;normal/abnormal collapse,~100sample R-centered beats;10,000 synthetic beats/class store. Additional MIT-BIH Arrhythmia check AppendixF. Lead selection,sample frequency,patient-separated split and exact sample counts not fully specified in methods.

**Evaluation metrics:** Beat-average DTW,curve Fréchet,Euclidean,RMSE,MAE,MSE,PRD; per-timepoint KL,JS,MMD,Wasserstein,KS,mean/variance/skew differences (AppendixTableIV). Feature distributions and correlations for R/P/Q/T intervals/amplitudes (TableII); R-amplitude matching error mV/counts; downstream accuracy,precision,recall,F1,MCC (TablesI,III,V–VII). These averaged-beat errors are not individual unpaired fidelity.

**Training objectives:** Diffusion/feature-generator training objectives inherited or insufficiently specified; no complete weighted training equation. Eq.1 weighted squared feature discrepancy is an inference-time beat-selection cost, NOT a neural training loss. Matching weights not enumerated (§III).

**Reported evidence:** Synthetic feature-based abnormal-class F1 .479 vs BRIDGE .470 and real .778 (TableIII); normal-class .956 vs .222 and real .906. Thus large overall gains do not imply near-real abnormal performance. No CIs or seeds specified. End-to-end comparison limited to5beats due to memory (§IV.E).

**Clinical utility, experts and privacy:** TSTR evaluated with balancedSVM,decision tree,naiveBayes,SVM. No blinded clinical or privacy-attack study. Long examples do not establish validated minute-scale HRV.

**Reproducibility:** Several unspecified choices in feature generator, split and loss; Appendix provides metric values and examples. No implementation inspected.

**Critical assessment:** Reviewer assessment: useful separation of morphology and temporal structure, but preserve rhythm distributions and report reused-beat rates to assess diversity beyond concatenated duration.
