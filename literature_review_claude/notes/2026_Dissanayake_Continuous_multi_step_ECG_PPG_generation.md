# Continuous multi-step ECG and PPG generation through latent disentanglement
- **ID / Year / Venue:** P161 / 2026 / Computers in Biology and Medicine
- **Model & task:** Hybrid (spectrogram autoencoder with disentangled subject/temporal codes, adversarially trained time-shift encoder, recurrent rollout); seed- and subject-conditioned multi-step ECG/PPG continuation, exploratory style transfer
- **Losses:** MSE reconstruction; subject CE; cyclic latent-swap reconstruction; conditional latent adversarial + latent MSE + shifted reconstruction; auxiliary reconstruction-adversarial
- **Evaluation:** peak cross-correlation ratio per step; NeuroKit2 R-peak ratio, R-peak deviation, RR error; PQRST delineation success; subject-ID train-synthetic/test-real F1; PPG BP ratio; t-SNE [fidelity, clinical, utility-TSTR, conditional]
- **Data:** EPHNOGRAM ECG (17 subjects); PhysioNet ABP PPG (7 subjects); leads: 1; fs: 1000 (ECG) / 1250 (PPG) Hz; length: 2.0 s steps, ~6 s reliable s
- **Notes:** ECG CorrX 0.81 / 0.58 / 0.42 / 0.20 over steps; R-peak deviation 0.23 s and RR error 0.27 s; subject-ID F1 31% synthetic vs 56% real. Within-recording, segment-level split with overlapping windows, no baseline generator, ad-hoc 0.30 threshold.
- **Takeaway for ECGEN-Eval:** For continuation/forecast-style generators ECGEN-Eval should offer step-wise paired metrics plus R-peak timing error and RR-error against the true continuation (reusing the clinical feature extractor), and warn when train/test windows come from the same recordings.
- *Extraction source: full-text*
