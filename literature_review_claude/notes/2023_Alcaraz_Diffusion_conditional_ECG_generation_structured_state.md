# Diffusion-based conditional ECG generation with structured state space models
- **ID / Year / Venue:** P168 / 2023 / Computers in Biology and Medicine
- **Model & task:** Diffusion (DDPM with structured state space S4 backbone, 'SSSD-ECG'); baselines WaveGAN*, Pulse2Pulse; class-cond (71 PTB-XL statements, multi-label)
- **Losses:** DDPM epsilon-prediction L2 loss (class-conditional)
- **Evaluation:** Classifier-based measures with XResNet1d50 macro AUROC over 71 labels: Train-synthetic/Test-real (TSTR), Train-real/Test-synthetic (TRTS) via fixed reference classifier, Train-synth/Test-synth internal consistency; qualitative beat-level quantile-band plots; conditional label interpolation; clinical Turing test with a cardiologist (44 ECGs, real vs synthetic + diagnosis)
- **Data:** PTB-XL; leads: 12 (8 generated: I, aVF, V1-V6; remaining 4 reconstructed from limb-lead relations); fs: 100; length: 10
- **Takeaway for ECGEN-Eval:** Adopt the TSTR/TRTS/TSTS triad with a fixed reference classifier; note TSTS is uninformative.
- *Extraction source: full-text*
