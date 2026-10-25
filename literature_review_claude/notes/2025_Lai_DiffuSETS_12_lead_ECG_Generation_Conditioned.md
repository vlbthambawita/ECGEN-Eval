# DiffuSETS: 12-lead ECG Generation Conditioned on Clinical Text Reports and Patient-Specific Information
- **ID / Year / Venue:** P049 / 2025 / arXiv
- **Model & task:** Diffusion (latent DDPM U-Net with cross-attention on LLM text embeddings + patient info; VAE latent space); task: text-cond
- **Losses:** Latent DDPM noise-prediction MSE ||ε-ε̂(z_t,t,c)||²; VAE: MSE reconstruction + λ·KL divergence
- **Evaluation:** Signal level: FID; improved precision/recall/F1 (Kynkäänniemi manifold) on embeddings; Feature level: heart-rate MAE (conditioned vs generated HR); Diagnostic level: CLIP score (text-ECG alignment); clinical Turing test (2 cardiologists, 50 real+50 generated); expert semantic-alignment check (100 ECGs, 76%); heart-age correlation via AnyECG (r=0.594); downstream augmentation classification for rare classes (tags: fidelity; distribution; clinical; utility-TSTR; expert)
- **Data:** MIMIC-IV-ECG (+ MIMIC-IV-Clinical for age/sex); PTB-XL (external); leads: 12; fs: 500 resampled to 1024 samples (~102.4) Hz; length: 10 s
- **Notes:** Proposes three-level benchmark (signal/feature/diagnostic). Argues MAE unreliable due to phase shifts, uses manifold P/R instead. MIMIC: FID 23.6, F1 0.894, HR-MAE 4.15, CLIP 0.812. Baselines WaveGAN, Pulse2Pulse, SSSD-ECG on PTB-XL.
- **Takeaway for ECGEN-Eval:** Adopt three-level protocol: embedding FID + manifold precision/recall, condition-adherence MAE (e.g., HR), and text/label alignment via a CLIP-style ECG-text encoder.
- *Extraction source: full-text*
