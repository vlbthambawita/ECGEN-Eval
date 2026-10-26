# CoFE: A Framework Generating Counterfactual ECG for Explainable Cardiac AI-Diagnostics
- **ID / Year / Venue:** P181 / 2025 / arXiv 2508.16033 (ACM-format demo paper, MedicalAI 2025)
- **Model & task:** StyleGAN2 generator of 12-lead ECG plus an inversion encoder; counterfactual ECGs are produced by gradient descent on the latent code so a pretrained AI-ECG model (AF classifier or potassium regressor) moves toward a target class, shown alongside saliency maps.
- **Losses:** Standard GAN adversarial loss; encoder L2 reconstruction loss; cross-entropy counterfactual loss on the latent code.
- **Evaluation:** Only clinical feature shifts (P-wave amplitude, RR variability, T-wave amplitude, QRS duration) between original and counterfactual ECGs on 1,000 MIMIC-IV recordings with p<0.05, plus qualitative saliency/counterfactual figures; no realism, distribution, diversity or expert evaluation of the generator.
- **Data:** MIMIC-IV-ECG (300k 12-lead ECGs at 250 Hz for the generator), PhysioNet/CinC 2017 for the AF classifier, MIMIC-IV ECG-potassium pairs; 10-s segments for the target models.
- **Takeaway for ECGEN-Eval:** Provide a paired original-vs-edited clinical-feature shift test (direction, magnitude and significance of interval/amplitude changes) for conditional or counterfactual generators.
- *Extraction source: full-text*
