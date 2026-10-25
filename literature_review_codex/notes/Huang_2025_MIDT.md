# High-Fidelity Synthetic ECG Generation via Mel-Spectrogram Informed Diffusion Training

**Citation:** Zhuoyi Huang and Nutan Sahoo and Anamika Kumari and Girish Kumar and Kexuan Cai and Shixing Cao and Yue Kang and Tian Xia and Somya Chatterjee and Nicholas Hausman and Aidan Jay and Eric S. Rosenthal and Soundar Srinivasan and Sadid Hasan and Alex Fedorov and Sulaiman Vesal. *High-Fidelity Synthetic ECG Generation via Mel-Spectrogram Informed Diffusion Training*. arXiv, 2025. DOI: not identified. arXiv: 2510.05492v2; first public: 2025-10-07; peer-reviewed date: not verified.

**Source/version:** [paper.pdf](../papers/2025/Huang_2025_MIDT/paper.pdf); [landing.html](../papers/2025/Huang_2025_MIDT/landing.html). [Landing page](https://arxiv.org/abs/2510.05492v2).


**Task and model:** SSSD-ECG with multiresolution mel-spectrogram supervision; diagnostic/form/rhythm groups and age/sex embeddings condition 12-lead generation (§3).

**Data and split:** PTB-XL 21,837 records/18,885 patients; 10 s at 100 Hz; explicitly patient-level 17,441/2,193/2,203 train/validation/test (§4). Age bins [12,17,34,54,74], sex 2 classes (§3.2). Additional normalization detail not reported in inspected methods.

**Evaluation metrics:** RMSE, MSE, SNR dB, Fourier distance, Hausdorff distance, SSIM; membership inference risk/MIR and nearest-neighbor adversarial accuracy/NNAA; mean/max absolute Pearson interlead correlation error; downstream AUROC with 95% CIs; qualitative outlier clinical-feature distributions (Tables1–4, Appendix A). Pairing/normalization and exact MIR/NNAA implementations are insufficiently specified. Paper marks MIR/NNAA lower as better; NNAA can be negative and is not simply classifier accuracy.

**Training objectives:** L_total=L_MSE+beta L_MIDT (Eq.1): multiresolution mel-magnitude L1 discrepancy between true and reconstructed ECG. Narrative calls MSE both denoising and signal-pointwise error; exact target is ambiguous. Beta, STFT window sizes, hop sizes and mel-bin count not reported; do not invent them (§3.1).

**Reported evidence:** Table2 average correlation error 0.140→0.042 (70% reduction, not abstract's 74%). Table4 synthetic-only AUROC 0.541±0.074→0.640±0.094; with 1 real fold MIDT 0.902±0.004 versus real-only 0.901±0.009. Large-real-data augmentation gains are small (Table3). Reported CIs and p<0.05 annotations lack clear run/test specification in these sections. Table1 MIR for MIDT 0.0081 exceeds gender variant 0.0036, contradicting prose calling MIDT lowest. Discussion makes further ablation/privacy-training claims without matching clearly specified training terms or tables (§5).

**Clinical utility, experts and privacy:** 8 synthetic folds plus increasing real folds, and 8 real folds plus 1–8 synthetic folds (Tables3–4). No formal blinded cardiologist experiment reported; visual examples are not a Turing test. MIR/NNAA are empirical proxies, not differential-privacy guarantees.

**Reproducibility:** Analyzed arXiv v2. Missing loss coefficient and spectral settings prevent exact paper-only reproduction. Demographic conditioning and loss changes require separate ablation; no code inspected.

**Critical assessment:** Reviewer assessment: evidence supports testing spectral supervision, but internal numerical/narrative inconsistencies and underdefined privacy metrics weaken strong trustworthiness claims.
