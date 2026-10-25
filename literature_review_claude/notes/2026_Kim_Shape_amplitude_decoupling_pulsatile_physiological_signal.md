# Shape and amplitude decoupling in pulsatile physiological signal synthesis and its evaluation
- **ID / Year / Venue:** P129 / 2026 / Nature communications
- **Model & task:** VAE (VABAM: variational framework with cascaded HPF/LPF filtering, bidirectional GRU, Gaussian shape latent z + uniform amplitude parameter theta); baselines ConVAE, FactorVAE, TCVAE, VDVAE, DiffWave, VDWave, WaveNet; other (amplitude-controllable synthesis with shape-amplitude decoupling; frequency-cutoff conditioning)
- **Losses:** ELBO with four terms: signal reconstruction log p(y|x); feature-subset reconstruction log p(x|z,theta) vs q(x|y,theta); KL(q(z|y)||N(0,I)); KL(q(theta|y)||Uniform) relaxed via reparameterized Bernoulli
- **Evaluation:** Five metrics: waveform shape factorization (SF), shape preservation / spectral distortion (SP/SD), amplitude modulation controllability (AC), spectral similarity (via conditional mutual information / KL on PSD permutation densities using FFT, DCT, Welch), reconstruction R2; composite ISCORE (arithmetic/geometric/harmonic mean of normalized metrics, Linfoot informational correlation normalisation)
- **Data:** MIMIC-III Waveform (ABP and ECG); VitalDB (ABP and ECG); cross-dataset train/test; leads: 1; fs: 100 (resampled from 125); length: 10 (compressed feature length 8 s at 100 Hz)
- **Takeaway for ECGEN-Eval:** Report spectral metrics under multiple PSD estimators and justify any composite score (AM/GM/HM sensitivity).
- *Extraction source: full-text*
