# Generation and Selection: A Self-Iterative Two-Stage Data Augmentation Method for Automated ECG Classification
- **ID / Year / Venue:** P082 / 2025 / IEEE Journal of Biomedical and Health Informatics
- **Model & task:** SiTs-ECG: unconditional DDPM with a Transformer-encoder noise predictor generates unlabeled ECG; a base classifier assigns pseudo-labels, keeps samples above confidence threshold 0.5, and retrains iteratively (re-labelling all generated samples each round)
- **Losses:** DDPM epsilon-MSE; classification loss with pseudo-labels
- **Evaluation:** Precision/Recall/F1/Accuracy with ResNet34 and ECG-Transformer; Context-FID; discriminative score; predictive score; PCA plots; paired t-test + Cohen's d; threshold and low-data ablations; runtime [utility-TSTR, distribution, fidelity, efficiency]
- **Data:** MIT-BIH (260-sample beats), Apnea-ECG (1-min), PTB-XL (12-lead, 100 Hz, 10 s); leads: 1 / 12; fs: 360 / 100 Hz; length: 0.72 / 60 / 10 s
- **Notes:** Apnea-ECG gains +7.9 P, +9.1 R, +9.2 F1, +7.3 Acc points (p < 0.05, d > 0.8); PTB-XL F1 0.801. Discriminative and predictive scores < 0.1; ECG-GAN Context-FID 37.4 on MIT-BIH. Quality tables are images, so most numbers are not recoverable from the text. Confidence filtering by the classifier itself keeps 'easy' samples and the base classifier implicitly acts as a quality metric.
- **Takeaway for ECGEN-Eval:** Context-FID, discriminative score and predictive score (the TimeGAN suite) are common in time-series papers, so ECGEN-Eval should offer a C2ST/discriminative score and a train-on-synthetic forecasting score, and should report how many generated samples a confidence filter kept, since filtering changes the evaluated distribution.
- *Extraction source: full-text*
