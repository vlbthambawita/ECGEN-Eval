# AI-based 3-Lead to 12-Lead ECG Reconstruction: Towards Smartphone-based Public Healthcare
- **ID / Year / Venue:** P016 / 2024 / arXiv
- **Model & task:** GAN (1D Pix2Pix conditional GAN, UNet generator, PatchGAN-style 1D interval discriminator); baselines LSTM, LSTM-UNet; lead-reconstruction (3-lead I, II, V2 -> 12-lead)
- **Losses:** not explicitly reported (1D Pix2Pix conditional adversarial objective implied)
- **Evaluation:** coefficient of determination R2; Pearson correlation coefficient rx; per-lead and per-diagnostic-subgroup (HC, BB, HY, MI, VA, ND) analysis
- **Data:** Train: SPH (Shaoxing), CPSC2018, Georgia, INCART; Test: PTB, PTB-XL; leads: 3 -> 12 (9 reconstructed); fs: 500 (PTB resampled from 1000); length: PTB-XL ~5 s records (as stated); PTB 30 s; sliding windows
- **Takeaway for ECGEN-Eval:** Report reconstruction metrics per lead and per diagnostic subgroup; R2 + Pearson are standard paired metrics for lead reconstruction.
- *Extraction source: full-text*
