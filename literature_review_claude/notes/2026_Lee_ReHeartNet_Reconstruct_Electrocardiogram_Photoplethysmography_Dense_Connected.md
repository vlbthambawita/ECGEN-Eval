# ReHeartNet: Reconstruct Electrocardiogram From Photoplethysmography by Using Dense Connected Deep Learning Model
- **ID / Year / Venue:** P127 / 2026 / IEEE Open Journal of Engineering in Medicine and Biology
- **Model & task:** Other (deterministic regression: densely connected BiLSTM, DC-BiLSTM); baselines GAN (CardioGAN), BiLSTM, Transformer; task: PPG2ECG
- **Losses:** RMSE reconstruction loss
- **Evaluation:** RMSE; Pearson correlation r; beat-timing error (mean absolute R-peak displacement, Pan-Tompkins, nearest-peak matching without tolerance window); 95% CIs across subjects; significance tests vs baselines (tags: fidelity; clinical)
- **Data:** MIMIC-III; BIDMC; TBME-RR; CBIC-Heart (new long-term dataset); leads: 1; fs: varies per dataset (not unified in text) Hz; length: not reported s
- **Notes:** Introduces beat-timing error since amplitude metrics miss R-peak displacement critical for HR/HRV. Cross-dataset sampling-rate differences used to test robustness.
- **Takeaway for ECGEN-Eval:** Add an R-peak beat-timing error metric for paired reconstruction tasks.
- *Extraction source: full-text*
