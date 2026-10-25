# Improving Diffusion Models for ECG Imputation with an Augmented Template Prior
- **ID / Year / Venue:** P093 / 2023 / arXiv
- **Model & task:** Diffusion (PulseDiff: CSDI and SSSD-S4 backbones conditioned on augmented pulse-template prior); imputation
- **Losses:** DDPM epsilon-prediction MSE conditioned on observed values and template prior p
- **Evaluation:** MSE (imputed vs ground truth); downstream multi-label classification macro-AUC (rhythm, form, diagnostic) with pretrained xResNet1d; beat detection F1, precision, sensitivity (SWT detector, 50 ms tolerance); evaluated at 10-50% missingness (transient and extended) [fidelity; utility-TSTR; clinical]
- **Data:** PTB-XL (PulseImpute splits: 8730 train / 2176 val / 10931 test); leads: 1 (single-channel); fs: 100 Hz; length: 10 s
- **Notes:** Follows PulseImpute benchmark. Transient 30%: PulseDiff-SSSDS4 MSE 0.0021; extended: 0.0192, deterministic BDC transformer still best. Notes diffusion trained on noise-space loss underperforms on long gaps.
- **Takeaway for ECGEN-Eval:** Beat-detection F1 with tolerance window and pretrained-classifier AUC on generated signals are reusable checks.
- *Extraction source: full-text*
