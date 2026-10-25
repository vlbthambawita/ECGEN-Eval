# Latent diffusion based hard sample generation for obstructive sleep apnea detection using single-lead ECG
- **ID / Year / Venue:** P098 / 2026 / IET conference proceedings.
- **Model & task:** Diffusion (latent feature diffusion model integrated with BAFNet); task: augmentation (hard-sample feature generation)
- **Losses:** unknown (abstract only)
- **Evaluation:** downstream OSA detection accuracy; sensitivity; F1-score (tags: utility-TSTR)
- **Data:** PhysioNet Apnea-ECG; leads: 1; fs: unknown (abstract only) Hz; length: unknown (abstract only) s
- **Notes:** Generates feature vectors (not waveforms) for hard samples near decision boundary; evaluated only by downstream classifier gains.
- **Takeaway for ECGEN-Eval:** Feature-space augmentation cannot be evaluated by waveform metrics; utility-only evaluation.
- *Extraction source: abstract-only*
