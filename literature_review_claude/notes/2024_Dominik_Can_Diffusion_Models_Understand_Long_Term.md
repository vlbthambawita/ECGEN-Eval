# Can Diffusion Models Understand the Long Term Dependencies in an ECG?
- **ID / Year / Venue:** P027 / 2024 / not reported
- **Model & task:** Diffusion (latent diffusion model); unconditional (long 5-min ECG)
- **Losses:** unknown (abstract only)
- **Evaluation:** HRV parameters (incl. HRV spectrum VLF power) compared to training set; mean heart-rate distribution comparison (incl. tails); rate of misrendered QRS complexes
- **Data:** unknown (abstract only); leads: unknown (abstract only); fs: unknown (abstract only); length: 300
- **Takeaway for ECGEN-Eval:** Add per-recording QRS-artifact rate and tail coverage checks (e.g., HR quantiles) alongside HRV distribution metrics for long ECGs.
- *Extraction source: abstract-only*
