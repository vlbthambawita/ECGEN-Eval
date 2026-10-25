# ECGTwin: Personalized ECG Generation Using Controllable Diffusion Model
- **ID / Year / Venue:** P067 / 2025 / arXiv
- **Model & task:** Diffusion (latent DDPM, DiT or U-Net backbone, AdaX condition injector; contrastive Individual Base Extractor); task: class-cond / text-cond (personalized ECG digital twin)
- **Losses:** Stage 1: symmetric CLIP-style InfoNCE contrastive loss (cosine similarity, learnable τ) on same-patient ECG pairs; Stage 2: DDPM noise-prediction MSE; pre-trained VAE decoder
- **Evaluation:** FID; improved precision/recall/F1 (Kynkäänniemi); HR-MAE; CLIP score; intra-/inter-individual similarity score (cosine); silhouette coefficient; t-SNE; downstream personalized normal/abnormal classification accuracy and macro-F1 (patient-wise and population-wise) (tags: fidelity; distribution; clinical; utility-TSTR)
- **Data:** MIMIC-IV-ECG (+ MIMIC-IV-Clinical); PTB-XL (external); leads: 12; fs: 102.4 (downsampled from 500; 1024 samples) Hz; length: 10 s
- **Notes:** Reuses DiffuSETS three-level evaluation; adds identity-preservation metrics (similarity score = mean intra-patient minus inter-patient cosine; silhouette). Baselines LAVQ, DiffuSETS-p. CLIP lower on PTB-XL due to German reports.
- **Takeaway for ECGEN-Eval:** For conditional/personalized generation, add identity-preservation metrics (intra- vs inter-subject embedding similarity, silhouette).
- *Extraction source: full-text*
