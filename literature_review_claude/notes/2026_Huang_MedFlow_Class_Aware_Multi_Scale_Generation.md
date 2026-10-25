# MedFlow: Class-Aware Multi-Scale Generation for Medical Time-Series Synthesis
- **ID / Year / Venue:** P102 / 2026 / arXiv
- **Model & task:** FlowMatching (class-aware multi-scale flow matching over VQ multi-scale token embeddings with Token Marginal Guidance; MedFlow); class-cond (medical time series incl. ECG; imbalanced classes)
- **Losses:** Stage 1 tokenizer: MSE reconstruction + cosine commitment loss (EMA codebooks); Stage 2: categorical endpoint cross-entropy loss (class-weighted) + structured-source prior regularizer (no direct velocity regression)
- **Evaluation:** TSTR AUROC; TSTR AUPRC; Discriminative Score (post-hoc GRU); Predictive Score; Context-FID (TS2Vec encoder, dim 320); t-SNE overlap; feature-wise moment, tail-quantile and minority-class statistic discrepancies; sampling throughput (tags: utility-TSTR;distribution;efficiency)
- **Data:** MIMIC-III; eICU (EHR); APAVA (EEG); PTB Diagnostic ECG (Medformer split, 108/29/61 subjects); leads: 15 (PTB channels); fs: not reported; length: single heartbeat (288 samples)
- **Notes:** For PTB ECG only TSTR AUROC/AUPRC reported; DS/PS/C-FID reported for EHR tasks. Claims avg -88.6% C-FID and 3.8x throughput vs TarDiff. Emphasises that global fidelity metrics can hide minority-class/tail failures.
- **Takeaway for ECGEN-Eval:** Add per-class / tail-quantile fidelity and Context-FID (TS2Vec) as a domain-agnostic embedding metric alongside ECG-specific FED.
- *Extraction source: full-text*
