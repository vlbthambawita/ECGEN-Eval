# Temporal Latent Priors Improve Sequential Generative Modeling of Full-Length 12-Lead ECGs
- **ID / Year / Venue:** P160 / 2026 / IEEE International Symposium on Computer-Based Medical Systems (CBMS)
- **Model & task:** VAE (sequential VAE, time-indexed latents; LSTM/BiLSTM/CNN-LSTM/Transformer encoders; i.i.d. vs learned autoregressive temporal prior; VAE/IWAE/IAF/InfoVAE-MMD objectives; dual reconstruction + classification head); unconditional full-length 12-lead modelling
- **Losses:** heteroscedastic Gaussian NLL + annealed KL + multi-label BCE; IWAE / IAF / InfoVAE-MMD variants
- **Evaluation:** reconstruction RMSE, PSNR, Pearson; macro-AUROC; latent active fraction; Holm-corrected statistical tests; visual inspection of samples [fidelity, utility-TSTR]
- **Data:** PTB-XL; leads: 12; fs: 100 Hz; length: 10 s
- **Notes:** Temporal prior lowers RMSE 16-18% and raises PSNR 1.5-1.7 dB; Transformer + InfoVAE-MMD best; AUROC ~0.91 unaffected. Every quantitative metric is on reconstructions; unconditional samples were unrealistic and only shown visually.
- **Takeaway for ECGEN-Eval:** A clear case where excellent paired reconstruction metrics (RMSE/PSNR/r ~0.99) coexist with unrealistic prior samples, so ECGEN-Eval docs should warn that psnr/mae on reconstructions are not generation quality and recommend running unpaired metrics (fed, mmd, sqi, clinical features) on prior samples.
- *Extraction source: full-text*
