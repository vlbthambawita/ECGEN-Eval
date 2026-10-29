# L2L-ESN: A Lead-to-Lead Electrocardiogram Synthesis Network for Assisting Myocardial Infarction Diagnosis
- **ID / Year / Venue:** P097 / 2026 / Intelligent Computing
- **Model & task:** Conditional WGAN-GP with 1D U-Net multihead generator (one output channel per target lead) and CNN critic on source+target leads; lead reconstruction II→7 key leads (1T7) or II+V1→6 (2T6), followed by MI detection/localisation
- **Losses:** Conditional Wasserstein + gradient penalty + MSE (50:1)
- **Evaluation:** Paired RMSE, PCC, curve Fréchet distance; per-lead MI detection with synthetic vs real lead; real+synthetic lead combinations for MI detection and AMI/IMI localisation; baselines SSSD-S4, ecg_recon, lead_recon; ablations; deployment profiling [fidelity, utility-TSTR, clinical, efficiency]
- **Data:** PTB-XL + private HeMI; leads: 1-2 in -> 6-7 generated (12 after deriving limb leads); fs: 100 Hz; length: 10 s
- **Notes:** 1T7 PTB-XL RMSE 0.158 / PCC 0.747 / FD 0.739, beating SSSD-S4 (0.163/0.737/0.825). Synthesized leads give MI-detection F1 close to but not above real leads; adding them to II+V1 helps modestly. Loss-weight ablation shows reconstruction metrics and diagnostic F1 disagree (1:1 best HeMI F1 85.7 but worst RMSE).
- **Takeaway for ECGEN-Eval:** The disagreement between waveform metrics and diagnostic F1 argues for ECGEN-Eval to pair per-lead mae/RMSE and correlation with a downstream-utility hook, and to add a paired curve Fréchet distance distinct from the distributional fd metric to avoid name confusion.
- *Extraction source: full-text*
