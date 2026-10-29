# Disentangled conditional generation of ECG signals with interpretable latent factors
- **ID / Year / Venue:** P051 / 2026 / Computer Methods and Programs in Biomedicine
- **Model & task:** Hybrid VAE + normalizing flow (Transformer beta-TC-VAE, 8-d latent, RealNVP-style class-conditional latent flow used only at sampling); class-conditional, interpretable single-beat generation (PTB-XL superclasses; MIT-BIH out-of-domain)
- **Losses:** beta-TCVAE (recon + alpha MI + beta TC + gamma dim-wise KL); flow trained with latent MMD + conditional NLL
- **Evaluation:** MIG / SAP / R² disentanglement; latent traversals and Jacobians; Fake-Test (TRTS) and Fake-Train (TSTR) RBF-SVM accuracies as fidelity/diversity; signal projections; class-mean waveforms; augmentation accuracy; Spearman with ECGdeli ST elevation [fidelity, diversity, utility-TSTR, conditional, robustness, clinical]
- **Data:** PTB-XL lead I; ECGSYN; MIT-BIH (out-of-domain); leads: 1; fs: 250 Hz; length: 1.0 s (single beat)
- **Notes:** Proxy MIG 0.53; Fake-Test/Fake-Train 44.4/45.3% with flow vs 20.0/17.9% from N(0,I) prior (5-class chance 20%); out-of-domain 66.3/80.1% vs 33.4/32.2%. Under the same protocol SSSD-ECG released samples score 48.6/47.0 and a retrained Pulse2Pulse/WaveGAN* 28.5/28.8. Augmentation gain is marginal (73.07 -> 73.70%).
- **Takeaway for ECGEN-Eval:** Add a classifier-based TRTS/TSTR (Fake-Test/Fake-Train) conditional metric with explicit chance level, since it exposed prior-sampling mode collapse to class-average beats that per-sample fidelity metrics would not flag.
- *Extraction source: full-text*
