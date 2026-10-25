# AI modeling photoplethysmography to electrocardiography useful for predicting cardiovascular disease
- **ID / Year / Venue:** P015 / 2025 / npj Digital Medicine
- **Model & task:** AR-Transformer (TimeVQVAE-style: STFT dual-band LF/HF VQ-VAE + bidirectional masked-token Transformers, PPG-conditioned via CLIP-style contrastive PPG encoder); Hybrid; task: PPG2ECG
- **Losses:** Stage 0: symmetric InfoNCE/CLIP contrastive loss (PPG-ECG, τ=0.05) + MAE reconstruction pretraining; Stage 1: VQ codebook + β-commitment loss + L2 reconstruction (ISTFT) for LF and HF; Stage 2: masked-token negative log-likelihood (cross-entropy) for LF/HF priors
- **Evaluation:** FID (on ROCKET features); Fréchet Distance on raw signals (FD); Marginal Distribution Difference (MDD); Autocorrelation Difference (ACD); Skewness Difference (SD); Kurtosis Difference (KD); MAE; MSE; PSNR; SSIM; downstream CVD screening AUC, sensitivity, specificity, accuracy, PPV, NPV, F1, kappa (DeLong, McNemar, bootstrap) (tags: fidelity; distribution; utility-TSTR)
- **Data:** PulseDB-MIMIC; PulseDB-VitalDB; MESA (pretraining); MIMIC-AF subset; private BBX smart-ring PPG-AF set; PPG-DaLiA; WESAD; leads: not reported; fs: 256 (PulseDB upsampled from 125) Hz; length: 10 s
- **Notes:** Uses TSGBench-style stats (MDD, ACD, SD, KD) alongside FID/FD/PSNR/SSIM; baselines RDDM, WGAN, RecQRS. ACD 0.367 vs 31.0 second-best; FID 0.001 vs 0.008. Primary aim is CVD prediction from PPG; generation is for interpretability.
- **Takeaway for ECGEN-Eval:** Add cheap time-series distribution stats (marginal-distribution, autocorrelation, skewness, kurtosis differences) and a ROCKET-feature FID variant.
- *Extraction source: full-text*
