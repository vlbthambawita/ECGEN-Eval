# ECGrecover: a Deep Learning Approach for Electrocardiogram Signal Completion
- **ID / Year / Venue:** P066 / 2024 / arXiv
- **Model & task:** Other (U-Net regression; compared with GAN baselines EKGAN, Pix2Pix, and CopyPaste); lead-reconstruction + imputation (missing segments within a lead; full leads from a single lead)
- **Losses:** Composite L = MSE + alpha * Pearson-correlation loss (1 - r); alpha ablated in {0, 0.1, 0.5, 1, inf}
- **Evaluation:** RMSE; maximum absolute error (MAE); DTW; Pearson correlation coefficient (PCC); delta-QT distance (neurokit2 Q and T peak detection per beat); SQI Avg-QRS and SQI Fuzzy (% unacceptable); downstream TdP-risk DenseNet accuracy with augmentation (5 seeds); statistical tests (p<2e-16) [fidelity; clinical; utility-TSTR]
- **Data:** Generepol (15,119 ECGs, 989 healthy subjects, before/after Sotalol); PTB-XL; LUDB; leads: 12 (8 recorded + 4 derived); fs: 500 (downsampled to 50 Hz, 512 points, for modelling) Hz; length: 10 s
- **Notes:** Delta-QT shows CopyPaste trivially preserves QT, a metric pitfall. Hybrid MSE+Pearson loss balances amplitude and synchrony; Pearson-only gives high PCC but poor other metrics. Expert cardiologists curated data. Augmentation raised TdP accuracy 92.47 -> 93.84%.
- **Takeaway for ECGEN-Eval:** Adopt delta-QT (and other interval deltas) via neurokit2 plus SQI scores (Avg-QRS, Fuzzy) as clinical fidelity checks.
- *Extraction source: full-text*
