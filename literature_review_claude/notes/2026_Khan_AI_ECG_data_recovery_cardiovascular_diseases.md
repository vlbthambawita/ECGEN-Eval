# AI based ECG data recovery and cardiovascular diseases classification (CEDRC-network)
- **ID / Year / Venue:** P013 / 2026 / Scientific reports
- **Model & task:** VAE (beta-VAE) vs Temporal Fusion Transformer, plus Transformer-based convolutional denoising AE (TCDAE); imputation (missing-segment recovery) + denoising + downstream classification
- **Losses:** TCDAE: frequency-weighted Huber + cosine similarity loss; VAE: reconstruction + beta*KL; TFT: quantile loss over leads and horizons (observed-mask indicator); classifiers: cross-entropy
- **Evaluation:** MAE; MSE; RMSE; NRMSE; Pearson correlation and energy difference (%) per lead (denoising); PSD comparison; downstream ML classification accuracy, F1 (AF, sinus bradycardia, tachycardia, sinus rhythm) at 10/30/50% missing; bootstrap (1000) accuracy SD; McNemar's test [fidelity; utility-TSTR]
- **Data:** MIMIC-IV-ECG (Diagnostic ECG Matched Subset), 2426 patients; leads: 12; fs: 500 Hz; length: 10 s
- **Notes:** TFT MAE 0.015, RMSE 0.0132 vs VAE MAE 0.075, RMSE 0.107; patient-level split; McNemar test for paired classifier comparison; bootstrap CIs. Evaluation is reconstruction-oriented, not generative distribution matching.
- **Takeaway for ECGEN-Eval:** Bootstrap CIs and McNemar's paired test are good statistical practice for utility comparisons in ECGEN-Eval reports.
- *Extraction source: full-text*
