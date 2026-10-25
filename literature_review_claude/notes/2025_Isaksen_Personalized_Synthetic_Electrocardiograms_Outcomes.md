# Personalized Synthetic Electrocardiograms with Outcomes
- **ID / Year / Venue:** P113 / 2025 / medRxiv
- **Model & task:** Personalized U-Net generator producing 1:1 synthetic ECGs linked to patient characteristics and outcomes
- **Losses:** Point-wise MSE (denoising from noised original)
- **Evaluation:** Bland-Altman of 12SL markers; association preservation (linear and Cox models); nearest-neighbour re-identification rate
- **Data:** GESUS, LOFUS (train), Inter99 (test); 12-lead, 500 Hz, 10 s
- **Takeaway for ECGEN-Eval:** Add epidemiological association-preservation tests and marker-space nearest-neighbour re-identification rate to ECGEN-Eval.
- *Extraction source: full-text*
