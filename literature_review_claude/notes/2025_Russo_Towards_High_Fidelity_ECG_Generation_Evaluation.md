# Towards High-Fidelity ECG Generation: Evaluation via Quality Metrics and Human Feedback
- **ID / Year / Venue:** P145 / 2025 / International Joint Conference on Biomedical Engineering Systems and Technologies (BIOSTEC)
- **Model & task:** Diffusion (SSSD-ECG, hyperparameter-optimized) + EvalOnly (DL quality evaluator); class-cond / evaluation
- **Losses:** unknown (abstract only; diffusion denoising objective of SSSD-ECG)
- **Evaluation:** quantitative fidelity metrics (unspecified); medical expert feedback; diversity; utility; learned DL evaluator classifying each synthetic ECG into 4 quality levels; correlation of evaluator with fidelity metrics [fidelity; expert; utility-TSTR; distribution]
- **Data:** unknown (abstract only; SSSD-ECG typically PTB-XL); custom 12-lead quality dataset with 4 quality levels; leads: 12; fs: unknown (abstract only) Hz; length: unknown (abstract only) s
- **Notes:** Proposes a learned per-sample quality metric (4 levels) trained on a purpose-built quality dataset, validated against fidelity metrics and experts.
- **Takeaway for ECGEN-Eval:** A learned per-sample quality score (like a SQI classifier) is worth adding as a per-sample metric alongside set-level ones.
- *Extraction source: abstract-only*
