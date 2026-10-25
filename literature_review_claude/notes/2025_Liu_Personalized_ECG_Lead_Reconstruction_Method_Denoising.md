# A Personalized ECG Lead Reconstruction Method Based on Denoising Diffusion Model
- **ID / Year / Venue:** P006 / 2025 / not reported
- **Model & task:** Diffusion (denoising diffusion model, conditional on lead II, with per-patient fine-tuning); lead-reconstruction
- **Losses:** unknown (abstract only)
- **Evaluation:** Pearson correlation coefficient (tags: fidelity)
- **Data:** PTB Diagnostic ECG Database; leads: 1 -> 12; fs: unknown (abstract only); length: unknown (abstract only)
- **Notes:** Personalized lead II -> 12-lead reconstruction; diffusion prior trained on full 12-lead data then fine-tuned with small amount of target-patient 12-lead data. Mean correlation 0.82 vs ground truth, outperforming DL baselines.
- **Takeaway for ECGEN-Eval:** Paired reconstruction metrics (per-lead Pearson r) belong in a paired/conditional-task mode; patient-wise splits matter.
- *Extraction source: abstract-only*
