# Beyond Single-Channel: Multichannel Signal Imaging for PPG-to-ECG Reconstruction with Vision Transformers
- **ID / Year / Venue:** P024 / 2025 / arXiv
- **Model & task:** Multichannel signal-imaging + ViT for PPG-to-ECG
- **Losses:** MSE + QRS-enhanced Gaussian-weighted loss
- **Evaluation:** PRD, RMSE, R/P/T-HRV, relative errors for QRS area, PR interval, RT interval, RT amplitude
- **Data:** BIDMC, CapnoBase (30 records each, leave-one-out), 125 Hz
- **Takeaway for ECGEN-Eval:** Clinical interval/amplitude relative-error metrics (PR, QRS area, RT) map well onto the features module for paired evaluation.
- *Extraction source: full-text*
