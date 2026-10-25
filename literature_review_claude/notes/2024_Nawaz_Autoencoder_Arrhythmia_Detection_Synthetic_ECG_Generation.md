# Autoencoder-based Arrhythmia Detection using Synthetic ECG Generation Technique
- **ID / Year / Venue:** P021 / 2024 / Annual International Conference of the IEEE Engineering in Medicine and Biology Society. IEEE Engineering in Medicine and Biology Society. Annual International Conference
- **Model & task:** GAN (+ autoencoder anomaly detector); augmentation (synthetic normal beats for anomaly detection)
- **Losses:** unknown (abstract only)
- **Evaluation:** AUC-ROC (0.6768); AUC-PR (0.8537) of AE anomaly detector trained only on synthetic normal data [utility-TSTR]
- **Data:** MIT-BIH Arrhythmia; leads: unknown (abstract only); fs: unknown (abstract only) Hz; length: unknown (abstract only) s
- **Notes:** Pure train-on-synthetic (normal only) anomaly detection; no direct signal-fidelity metrics mentioned in abstract. Low AUROC.
- **Takeaway for ECGEN-Eval:** TSTR variant: train a one-class/anomaly model on synthetic normals and test on real normal+abnormal.
- *Extraction source: abstract-only*
