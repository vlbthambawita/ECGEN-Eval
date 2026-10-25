# TransDiffECG: Semantically controllable ECG synthesis via transformer-based diffusion modeling
- **ID / Year / Venue:** P146 / 2025 / Journal of Biomedical Informatics
- **Model & task:** Diffusion (Transformer-based diffusion with semantic information injection); task: class-cond / semantic-controllable (fiducial-level control)
- **Losses:** unknown (abstract only)
- **Evaluation:** MMD; Pearson correlation; downstream segmentation precision/recall (train on synthetic only); AF classification AUROC with augmentation (tags: fidelity; distribution; utility-TSTR)
- **Data:** QTDB (single-lead); LUDB (multi-lead); leads: 1 and 12; fs: unknown (abstract only) Hz; length: unknown (abstract only) s
- **Notes:** LUDB: MMD 3.21e-2, Pearson 0.6177; augmentation AF AUROC 0.9451; segmentation model trained only on synthetic ~98% precision/recall on QTDB (rivaling real). Same group as P012 metrics review.
- **Takeaway for ECGEN-Eval:** Segmentation-based TSTR (delineation model trained on synthetic) is a useful morphology-aware utility test.
- *Extraction source: abstract-only*
