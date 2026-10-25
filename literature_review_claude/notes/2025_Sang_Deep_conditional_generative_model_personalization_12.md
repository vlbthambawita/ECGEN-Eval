# Deep conditional generative model for personalization of 12-lead electrocardiograms and cardiovascular risk prediction
- **ID / Year / Venue:** P042 / 2025 / Frontiers in digital health
- **Model & task:** VAE (conditional VAE, 1D conv encoder/decoder) + Cox proportional-hazards head; other (personalised generation conditioned on demographics, heart pose, electrode positions; CVD risk prediction)
- **Losses:** cVAE ELBO: MSE reconstruction + KL divergence; plus Cox partial-likelihood survival loss; Ltotal = Lrecons + LKL + Lsurv (equal weights)
- **Evaluation:** qualitative comparison of morphology trends (R/S/T amplitudes per lead) against in silico simulation under heart rotation/translation; C-index for CVD risk; Kaplan-Meier stratification (tags: clinical;utility-TSTR)
- **Data:** UK Biobank (37,508 volunteers; 21,083 with ECG+MRI; 1,834 with electrode positions); in silico simulations (Mincholé et al.); leads: 12; fs: 500; length: median beat (~600 samples, model input 12x400); 10 s raw available
- **Notes:** No quantitative generative-quality metric; validation is lead-wise agreement of amplitude trends with biophysical simulation (often only partially agrees). C-index 0.63-0.65 from latent embeddings.
- **Takeaway for ECGEN-Eval:** Simulation-consistency (controllability: does changing a condition shift morphology as physics predicts) is a distinct evaluation axis.
- *Extraction source: full-text*
