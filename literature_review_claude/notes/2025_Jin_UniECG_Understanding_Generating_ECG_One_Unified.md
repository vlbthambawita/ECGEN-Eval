# UniECG: Understanding and Generating ECG in One Unified Model
- **ID / Year / Venue:** P149 / 2025 / arXiv
- **Model & task:** LLM (unified multimodal LLM with special ECG tokens mapped to frozen DiffuSETS text-conditioned latent diffusion; 'UniECG'); text-cond (also ECG interpretation)
- **Losses:** Weighted NLL for ECG_START/ECG token emission (L_e) + MSE between mapper output and frozen DiffuSETS text embedding (L_d)
- **Evaluation:** FID; Precision; Recall; F1 (signal-level, precision/recall-based); HR MAE; CLIP score (ECG-text); generation success rate; explanation scored by LLM judge (GLM-5) under ECG-R1 rubric
- **Data:** MIMIC-IV-ECG (737,875 training; 10,000 held-out eval); GEM test set (2,381) for explanation; leads: 12; fs: not reported (DiffuSETS protocol); length: not reported (DiffuSETS protocol, 10 s 12-lead implied)
- **Takeaway for ECGEN-Eval:** Report precision/recall alongside FID to separate realism from coverage; 'generation success rate' for LLM-driven generators.
- *Extraction source: full-text*
