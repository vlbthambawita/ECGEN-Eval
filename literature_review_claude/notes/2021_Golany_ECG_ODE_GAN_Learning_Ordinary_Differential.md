# ECG ODE-GAN: Learning Ordinary Differential Equations of ECG Dynamics via Generative Adversarial Learning
- **ID / Year / Venue:** P172 / 2021 / Proceedings of the AAAI Conference on Artificial Intelligence
- **Model & task:** GAN (ODE-GAN: generator learns ECG dynamics dh/dt solved with Euler ODE steps; physics-informed with McSharry simulator parameters); class-cond (per-heartbeat-class generators) + augmentation
- **Losses:** standard cross-entropy adversarial losses (generator and discriminator); baselines DCGAN cross-entropy, WGAN EM distance
- **Evaluation:** downstream heartbeat classification (1D-ResNet) trained on real + synthetic: per-class precision-recall curves and operating points (Re, Pr) per AAMI standard [utility-TSTR]
- **Data:** MIT-BIH Arrhythmia (AAMI inter-patient partition; N, S, V, F); leads: 1; fs: 360 Hz; length: 0.6 (216 samples, -200 to +400 ms around R-peak) s
- **Notes:** Evaluation purely by augmentation benefit (TRTR vs augmented), following SimGAN practice; no direct fidelity or distribution metric. e.g., SVEB (Re 0.40, Pr 0.83) vs SimGAN Pr 0.70. Patient-wise AAMI split.
- **Takeaway for ECGEN-Eval:** Augmentation-utility with patient-wise AAMI splits and per-class PR curves is the standard beat-level utility protocol.
- *Extraction source: full-text*
