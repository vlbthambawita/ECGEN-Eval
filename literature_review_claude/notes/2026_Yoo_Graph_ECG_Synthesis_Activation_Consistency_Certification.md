# Graph-Based ECG Synthesis with Activation-Consistency Certification and Diagnostics-Aware Morphology Curation
- **ID / Year / Venue:** P088 / 2026 / arXiv
- **Model & task:** Other (biophysical graph-based simulator: Eikonal-template ET and pseudo-diffusion reaction-Eikonal RE backends; not a deep generative model); other (mechanistic synthetic ECG generation + curation; synthetic pretraining)
- **Losses:** none for generator (simulation); delineation segmentation model loss not reported
- **Evaluation:** Bellman residual certificate (activation-time consistency); R² of RE vs Eikonal activation times; activation-order diagnostics; P/QRS/T amplitudes, intervals, polarity checks, morphology-failure flags; recovery plausibility score; feature-space coverage (fraction of occupied feature bins); acceptance yield; P/QRS/T delineation IoU after synthetic pretraining on 1-10% PTB-XL+ labels (tags: clinical;utility-TSTR;distribution)
- **Data:** simulated 12-lead ECGs; PTB-XL+ (delineation fine-tuning/evaluation); leads: 12; fs: not reported; length: single beats; 12 s concatenated traces for pretraining
- **Notes:** Two-stage diagnostics (metric computation separated from acceptance policy). Acceptance 658/2000 RE vs 578/2000 ET; coverage 0.09888 vs 0.09248. Synthetic pretraining stabilised low-label delineation (T-wave IoU std ≤0.003 vs 0.247). Not a learned generator; relevant mostly for curation/validity filters.
- **Takeaway for ECGEN-Eval:** Hard validity filters (flatline, missing QRS, inverted QRS) + binned feature-space coverage are useful sanity/diversity metrics.
- *Extraction source: full-text*
