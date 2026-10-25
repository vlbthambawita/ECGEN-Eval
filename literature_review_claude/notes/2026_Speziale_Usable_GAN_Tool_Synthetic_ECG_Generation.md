# A Usable GAN-Based Tool for Synthetic ECG Generation in Cardiac Amyloidosis Research
- **ID / Year / Venue:** P009 / 2026 / arXiv
- **Model & task:** GAN (vanilla GAN, BiLSTM generator/discriminator, class-specific); class-cond (beat augmentation; tool for cardiac amyloidosis)
- **Losses:** standard BCE adversarial loss (D: real/fake BCE; G: non-saturating BCE)
- **Evaluation:** Planned only: DTW; discrete Fréchet distance; Euclidean distance; nearest-synthetic-neighbour distance (median/IQR); productivity rate (fraction of real beats within 95th-pct real-real distance of a synthetic beat); KS test + Cohen's d on QRS duration, R amplitude, QRS area, ST level, T amplitude; Hotelling T²; energy distance; MMD on embeddings; accuracy, sensitivity, specificity, F1, AUROC, AUPRC; Brier score; ECE; decision-curve analysis; silhouette, Davies-Bouldin, ARI, bootstrap Jaccard cluster stability (tags: fidelity;distribution;clinical;utility-TSTR)
- **Data:** MIT-BIH Arrhythmia (Kaggle-style 187-sample beat CSV); planned CA cohorts; leads: 1; fs: not reported (187 samples per beat); length: single beat (187 samples)
- **Notes:** No quantitative results; evaluation protocol is planned. Interesting ideas: 'productivity rate' coverage metric, calibration (Brier/ECE) of augmented classifiers, cluster-stability of augmented data.
- **Takeaway for ECGEN-Eval:** Adopt 'productivity rate' (coverage of real samples within real-real 95th-percentile radius) and KS+Cohen's d per clinical feature.
- *Extraction source: full-text*
