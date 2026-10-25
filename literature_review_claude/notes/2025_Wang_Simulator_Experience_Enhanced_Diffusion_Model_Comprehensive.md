# Simulator and Experience Enhanced Diffusion Model for Comprehensive ECG Generation
- **ID / Year / Venue:** P130 / 2025 / arXiv
- **Model & task:** Diffusion (latent DDPM in VAE latent space, ODE-simulator-enhanced, LLM-powered EHR retrieval; 'SE-Diff'); text-cond (clinical text/metadata to 12-lead ECG)
- **Losses:** VAE: full reconstruction + β-KL + beat-decoder loss + log-spectrum (rFFT) band-weighted spectral loss; Diffusion: L_DDPM + λ simulator-guided Euler ODE-consistency loss + γ inter-lead (Einthoven/Goldberger) consistency loss
- **Evaluation:** Per-lead MAE; NRMSE; Pearson r; HR MAE (MAE_HR); relative CLIP score (rCLIP = s(gen,text)/s(real,text)); relative FID (rFID = FID(gen,real)/FID(real split1, real split2)) in ECG embedding space; downstream F1, Accuracy, AUROC for imbalanced sex and SVT classification
- **Data:** MIMIC-IV-ECG (800,035 ECGs); MIMIC-IV-Clinical (EHR retrieval); leads: 12; fs: 500; length: 10
- **Takeaway for ECGEN-Eval:** Implement rFID (FID normalised by real-split FID) and inter-lead Einthoven/Goldberger residual metrics; rCLIP for text-conditioned models.
- *Extraction source: full-text*
