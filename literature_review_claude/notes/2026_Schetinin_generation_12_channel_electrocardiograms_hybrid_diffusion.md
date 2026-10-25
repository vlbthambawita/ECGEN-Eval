# On the generation of 12-channel electrocardiograms based on a hybrid of diffusion and graph neural network models
- **ID / Year / Venue:** P108 / 2026 / VESTNIK OF ASTRAKHAN STATE TECHNICAL UNIVERSITY SERIES MANAGEMENT COMPUTER SCIENCE AND INFORMATICS
- **Model & task:** VAE-GNN-SSSD hybrid for 10 s 12-lead ECG conditioned on clinical parameters
- **Losses:** unknown
- **Evaluation:** FID, PRD, Einthoven-law MSE, Macro F1 augmentation
- **Data:** PTB-XL, MIT-BIH, MIMIC-IV-ECG
- **Takeaway for ECGEN-Eval:** Adopt an Einthoven/Goldberger lead-consistency metric (e.g. MSE of III-(II-I), aVR+aVL+aVF) for 12-lead synthesis.
- *Extraction source: abstract-only*
