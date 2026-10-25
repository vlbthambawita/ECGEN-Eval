# Exploring latent diffusion models for ECG generation on the minute scale
- **ID / Year / Venue:** P074 / 2025 / Computer Methods and Programs in Biomedicine
- **Model & task:** Diffusion (latent: VQ-VAE encoder + DDIM latent backbone; ECGEN); class-cond (sinus vs AFib); imputation (inpainting); unconditional long-duration
- **Losses:** unknown (abstract only) (VQ-VAE + diffusion objectives implied)
- **Evaluation:** heart rate (HR); HRV (SDNN etc.) distributions; morphological coherence; AFib vs sinus classification AUC (tags: clinical;utility-TSTR)
- **Data:** clinical ECGs from stroke patients; leads: unknown (abstract only); fs: unknown (abstract only); length: 30; 90; 320
- **Notes:** Minute-scale generation (up to 320 s). AUC 0.98 AFib vs SR. Long model showed inflated SDNN — HRV distribution shift reveals poor long-range temporal modelling; short-window metrics would miss this.
- **Takeaway for ECGEN-Eval:** HRV distribution metrics (SDNN) are essential for long recordings; already in hrv metric — emphasise for long signals.
- *Extraction source: abstract-only*
