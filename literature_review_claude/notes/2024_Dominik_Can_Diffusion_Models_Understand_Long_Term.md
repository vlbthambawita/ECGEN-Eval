# Can Diffusion Models Understand the Long Term Dependencies in an ECG?
- **ID / Year / Venue:** P027 / 2024 / Proceedings of the Workshop Biosignal 2024 (Göttingen)
- **Model & task:** Diffusion (latent diffusion: VQ-VAE on 2 s windows, latents concatenated over 320 s, DDIM denoiser); unconditional long (320 s) ECG generation, inpainting showcased
- **Losses:** not reported (standard VQ-VAE + DDIM denoising objectives implied)
- **Evaluation:** HRV parameters (time/frequency incl. VLF/LF/HF) vs training set; cumulative HRV distributions; mean heart-rate distribution (3,456 vs 3,456); misrendered-QRS rate; visual inspection [clinical, distribution]
- **Data:** Synthetic training set only (3,456 noise-free 320 s ECGs from ECGSYN BBI series + idealised QRS library); leads: 1 (implied); fs: 1024 Hz; length: 320 s
- **Notes:** ~30% of generated ECGs had >=1 misrendered QRS, causing ~1 s BBI gaps and spurious VLF HRV power. Mean HR 70.91 vs 70.67 BPM, but tails under-represented, visible only in cumulative distributions. VQ-VAE 2 s window seams produce periodic disturbances. No real ECG data and no baselines (workshop abstract).
- **Takeaway for ECGEN-Eval:** Report full distribution/tail comparisons (e.g. quantile or KS on per-recording HR/HRV, not just means) and add a beat-validity check (fraction of recordings with missed/misrendered QRS or implausible RR gaps) since a single bad beat corrupts HRV metrics.
- *Extraction source: full-text*
