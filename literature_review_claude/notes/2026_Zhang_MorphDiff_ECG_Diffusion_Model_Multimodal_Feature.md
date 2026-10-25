# MorphDiff-ECG: A Diffusion Model for Multimodal Feature Fusion of ECG Signals
- **ID / Year / Venue:** P105 / 2026 / IEEE Transactions on Biomedical Engineering
- **Model & task:** Diffusion (MorphDiff-ECG: trend/periodic/morphology decoupling + cross-feature attention fusion); class-cond / unconditional ECG generation (beats/segments)
- **Losses:** Hybrid: diffusion objective with time-domain reconstruction loss + wavelet-based time-frequency loss
- **Evaluation:** PRD; FD (Fréchet distance); RMSE; MAE
- **Data:** MIT-BIH; CPSC2020; nine-class CPSC2018; leads: unknown (abstract only); fs: unknown (abstract only); length: unknown (abstract only)
- **Takeaway for ECGEN-Eval:** PRD/FD/RMSE/MAE quartet is the de-facto comparison set; ECGEN-Eval should support it for comparability.
- *Extraction source: abstract-only*
