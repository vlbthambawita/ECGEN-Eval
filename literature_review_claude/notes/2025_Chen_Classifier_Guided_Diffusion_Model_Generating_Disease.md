# Classifier-Guided Diffusion Model for Generating Disease-Specific ECG Data: A Case Pilot Study on Inferior Myocardial Infarction
- **ID / Year / Venue:** P033 / 2025 / Annual International Conference of the IEEE Engineering in Medicine and Biology Society. IEEE Engineering in Medicine and Biology Society. Annual International Conference
- **Model & task:** Diffusion (classifier-guided); class-cond (disease-specific: inferior MI)
- **Losses:** unknown (abstract only)
- **Evaluation:** IMI-vs-normal classifier performance trained on real vs real+synthetic (TRTR vs TSRTR mix); statistical distribution comparison of Q-wave depth (real vs synthetic IMI) [utility-TSTR; clinical]
- **Data:** PTB-XL; leads: unknown (abstract only; likely 12); fs: unknown (abstract only) Hz; length: unknown (abstract only) s
- **Notes:** Uses a disease-specific clinical feature (Q-wave depth) distribution as fidelity evidence, a pathology-targeted clinical metric.
- **Takeaway for ECGEN-Eval:** Add pathology-specific clinical feature distribution checks (e.g., Q-wave depth for MI) to the feature-extraction suite.
- *Extraction source: abstract-only*
