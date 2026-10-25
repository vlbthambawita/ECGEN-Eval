# Versatile Cardiovascular Signal Generation with a Unified Diffusion Transformer
- **ID / Year / Venue:** P152 / 2025 / arXiv
- **Model & task:** UniCardio: unified multi-modal diffusion transformer for denoising, imputation and translation across PPG, ECG, BP
- **Losses:** Diffusion noise-prediction MSE; continual learning schedule
- **Evaluation:** RMSE, MAE, shift-tolerant Min-RMSE/Min-MAE, KS-test; downstream detection accuracy/sens/spec, HR and BP MAE; clinician review
- **Data:** Cuffless BP, PTB-XL, MIMIC PERform AF, WESAD, MIMIC; 4 s segments
- **Takeaway for ECGEN-Eval:** Adopt shift-tolerant (min over lags) RMSE/MAE for paired tasks and task-substitution utility tests.
- *Extraction source: full-text*
