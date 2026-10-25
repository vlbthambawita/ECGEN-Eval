# Invertible Conditional Generative Adversarial Networks to Effectively Generate Myocardial Infarction from Normal ECG
- **ID / Year / Venue:** P095 / 2025 / not reported
- **Model & task:** GAN (Invertible conditional GAN, IcGAN; compared with CycleGAN); other (style transfer NSR -> MI heartbeat)
- **Losses:** unknown (abstract only)
- **Evaluation:** visual inspection; GAN-train; GAN-test; ST-segment amplitude comparison (tags: utility-TSTR;clinical;fidelity)
- **Data:** PTB-XL; leads: 12; fs: unknown (abstract only); length: heartbeat
- **Notes:** Same group as P073. GAN-train (train on synth/test real) and GAN-test (train real/test synth) plus clinically targeted ST amplitude check for MI.
- **Takeaway for ECGEN-Eval:** Pathology-specific clinical feature checks (ST deviation for MI) complement generic metrics.
- *Extraction source: abstract-only*
