# Electrocardiogram Synthesis from Photoplethysmogram Signals Through Generative Adversarial Networks
- **ID / Year / Venue:** P068 / 2026 / IEEE LASCAS 2026
- **Model & task:** CardioGAN-style GAN (Attention U-Net generator, time- and frequency-domain discriminators); PPG→ECG translation with a custom synchronized acquisition rig
- **Losses:** LSGAN adversarial + L1
- **Evaluation:** MSE, Pearson ρ, (1−MSE)% similarity, filter SNR gain, qualitative time/frequency plots; comparison against published CardioGAN and Belhasin numbers [fidelity]
- **Data:** BIDMC, CapnoBase, PPG-DaLiA, WESAD + custom MAX30100/AD8232 recordings; leads: 1; fs: 128 Hz; length: 2 s (256 samples)
- **Notes:** MSE 0.278, ρ 0.68, similarity 72.2%; between Belhasin (0.222/0.71) and Sarkar (0.364/0.63) using copied numbers with different preprocessing. No subject split, HR or interval metrics reported.
- **Takeaway for ECGEN-Eval:** For PPG→ECG translation ECGEN-Eval should supplement paired MSE/correlation with heart_rate and R-peak timing agreement, and warn that '(1−MSE)% similarity' on z-scored data is not a valid fidelity score.
- *Extraction source: full-text*
