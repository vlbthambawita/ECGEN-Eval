# SSSD-ECG-nle: New Label Embeddings with Structured State-Space Models for ECG generation
- **ID / Year / Venue:** P134 / 2024 / arXiv
- **Model & task:** Diffusion (SSSD-ECG with new label embeddings 'nle': separate embeddings for label presence/absence; S4 backbone); class-cond (multi-label PTB-XL statements)
- **Losses:** DDPM epsilon-prediction MSE
- **Evaluation:** TSTR and TRTS with xResNet1d50 (binary per pathology: AFIB, CRBBB, PVC, 1AVB, CLBBB): G-mean, F1-score; multilabel TSTR/TRTS weighted G-mean, F1, ROC-AUC; real-data augmentation with synthetic positives; convergence analysis over training checkpoints; physician evaluation: text-report diagnosis accuracy on 100 real + 100 synthetic, and direct real-vs-synthetic discrimination (380 ECGs) confusion matrix [utility-TSTR; expert]
- **Data:** PTB-XL (folds 1-8 train, 9 val, 10 test); leads: 12 (8 generated, 4 derived); fs: 100 Hz; length: 10 s
- **Notes:** Key pitfall: good TSTR yet physicians identified synthetic ECGs almost perfectly (279/280 synthetic, 99/100 real correct); cues were low voltage, apparently reversed chest electrodes, artefacts. Authors dropped relation metrics (DTW, MMD, Wasserstein) and TSTS as 'uninformative'.
- **Takeaway for ECGEN-Eval:** TSTR alone is insufficient; add realism detectors (low-voltage, lead-reversal/inter-lead consistency checks) and a real-vs-synthetic classifier score.
- *Extraction source: full-text*
