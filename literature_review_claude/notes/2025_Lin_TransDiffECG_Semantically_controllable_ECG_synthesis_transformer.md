# TransDiffECG: Semantically controllable ECG synthesis via transformer-based diffusion modeling
- **ID / Year / Venue:** P146 / 2025 / Journal of Biomedical Informatics
- **Model & task:** Diffusion (DDPM on SSSD-ECG backbone; Transformer encoder/decoder + Semantic ECG Batch Normalization conditioned on P/QRS/T segmentation masks); fiducial-level controllable synthesis (HR, QTc) and augmentation
- **Losses:** DDPM noise-prediction MSE
- **Evaluation:** MMD; paired Pearson correlation; U-Net P/QRS/T onset/offset precision/recall (R->S and S->R); AF AUROC with augmentation; HR/QTc controllability (visual); membership inference AUROC [fidelity, distribution, clinical, utility-TSTR, conditional, privacy]
- **Data:** QTDB (single-lead); LUDB (12-lead, patient-wise 5-fold CV); leads: 1 and 12; fs: not reported in main text Hz; length: not reported in main text s
- **Notes:** LUDB MMD 3.21e-2, PC 0.6177 (best vs WaveGAN, P2PGAN, SSSD-ECG, DiffECG); QTDB S->R segmentation ~98% precision/recall matching real; AF AUROC 0.9451 vs 0.9004 real-only; MIA AUROC ~0.5. Baselines re-conditioned by the authors; PC is paired with the mask-source record; controllability not quantified.
- **Takeaway for ECGEN-Eval:** For mask/fiducial-conditioned generators, ECGEN-Eval's feature extractor could provide a conditional-adherence metric (delineated onsets/offsets or HR/QTc of synthetic vs requested values, with AAMI-style tolerances), and reports should flag paired Pearson as a reconstruction rather than distribution metric.
- *Extraction source: full-text*
