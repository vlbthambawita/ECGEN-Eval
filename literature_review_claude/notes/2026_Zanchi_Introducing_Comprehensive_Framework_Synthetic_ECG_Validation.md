# Introducing a Comprehensive Framework for Synthetic ECG Validation
- **ID / Year / Venue:** P094 / 2026 / IEEE open journal of engineering in medicine and biology
- **Model & task:** EvalOnly (validation framework; applied to Pulse2Pulse GAN Brugada ECGs); task: evaluation
- **Losses:** n/a (Pulse2Pulse WGAN-GP referenced)
- **Evaluation:** Four layers: (1) visual inspection; (2) morphology via NeuroKit on lead II: RR, PR, QRS, QT, QTc (Bazett), P/QRS/T axes, Mann-Whitney U; (3) similarity: Euclidean distance, maximum absolute error, cosine similarity, MSE, RMSE, NRMSE, RMSPE, kernel MMD, KL divergence, DTW (KMMD/KL/DTW on II, V1, V2) benchmarked against R-vs-R intra-subject and inter-subject distances; (4) expert cardiologist scoring (tags: fidelity; distribution; clinical; expert)
- **Data:** Private Brugada type-I 12-lead ECGs (21 patients, 1122 10-s windows with 50% overlap) vs 1122 synthetic; leads: 12; fs: not reported Hz; length: 10 s
- **Notes:** Only supplementary text available. Key idea: synthetic-to-real distance should lie between real intra-subject and inter-subject variability (R-vs-R benchmarking). Careful statistics: patient-level median aggregation to respect independence. Mentions EU AI Act/GMLP as validation gate.
- **Takeaway for ECGEN-Eval:** Adopt R-vs-R reference bands: express every distance metric relative to real intra-subject and inter-subject baselines.
- *Extraction source: full-text*
