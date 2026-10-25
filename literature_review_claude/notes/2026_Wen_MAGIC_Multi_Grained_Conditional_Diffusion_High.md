# MAGIC: Multi-Grained Conditional Diffusion for High-Fidelity PPG-to-ECG Translation
- **ID / Year / Venue:** P101 / 2026 / IEEE journal of biomedical and health informatics
- **Model & task:** Diffusion (Diffusion Transformer with multi-grained conditioning: AdaLN global + gated cross-attention local; pre-trained conditional encoder); PPG2ECG
- **Losses:** diffusion denoising objective; encoder pre-training with ROI-weighted reconstruction + contrastive loss + latent alignment
- **Evaluation:** FD (Frechet distance); four downstream proxy tasks (task-level utility); sampling steps comparison
- **Data:** four public datasets incl. MIMIC-AFib (others unknown (abstract only)); leads: 1 (implied, PPG->ECG); fs: unknown (abstract only); length: unknown (abstract only)
- **Takeaway for ECGEN-Eval:** FD plus steps-vs-quality efficiency curves; downstream proxy tasks as utility for translation models.
- *Extraction source: abstract-only*
