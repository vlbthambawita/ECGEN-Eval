# Structure-preserving adversarial multi-segment framework for bidirectional ECG–SCG signal translation
- **ID / Year / Venue:** P186 / 2026 / Biomedical Signal Processing and Control
- **Model & task:** GAN (CycleGAN with residual self-attention generators and multi-segment vectored-output discriminators); bidirectional SCG↔ECG translation
- **Losses:** least-squares adversarial + paired MSE + cycle-consistency + identity losses
- **Evaluation:** RMSE; PRD; MAE; Pearson correlation per subject/state; module and window-length ablations; qualitative plots [fidelity, conditional]
- **Data:** CEBS (20 healthy subjects, 3 states); leads: 1; fs: 1000 Hz; length: 1 s
- **Notes:** SCG→ECG RMSE 0.177, PRD 2.06%, PCC 0.978 vs 0.434/4.51/0.89 for the prior attentive CycleGAN; ECG→SCG PCC ~0.81-0.89 with some subject failures. Random within-subject 75/25 segment split means adjacent windows of the same recording appear in train and test; no beat-level clinical or distributional metrics.
- **Takeaway for ECGEN-Eval:** For paired translation tasks, ECGEN-Eval should require subject-disjoint test sets in reports and complement PRD/PCC with fiducial (R-peak, interval) agreement, since near-perfect PCC on within-subject splits says little about generalisation.
- *Extraction source: full-text*
