# Condition-fusion-and-hiding denoising diffusion model for electrocardiogram lead reconstruction
- **ID / Year / Venue:** P037 / 2026 / iScience
- **Model & task:** Diffusion (CFH-DDPM: condition-fusion-and-hiding DDPM); baselines VAE, EKGAN, DDPM; task: lead-reconstruction
- **Losses:** not reported
- **Evaluation:** Per-lead Sum of Squared Difference (SSD); Percentage Root-mean-square Difference (PRD %); Cosine Similarity (%); Signal-to-Noise Ratio (SNR dB) (tags: fidelity)
- **Data:** PTB-XL; CPSC2018; leads: 12 (input lead I implied by near-perfect lead I scores); fs: not reported Hz; length: not reported s
- **Notes:** Only supplementary tables available. CFH-DDPM mean PTB-XL: SSD 31.84, PRD 73.78%, COS 68.59%, SNR 4.79 dB; EKGAN has lower PRD (69.78%). Limb leads III/aVF show PRD >100% for all models, showing PRD saturates for poorly predictable leads.
- **Takeaway for ECGEN-Eval:** Report reconstruction metrics per lead: averages hide that some leads (III, aVF) are essentially unpredictable (PRD>100%).
- *Extraction source: full-text*
