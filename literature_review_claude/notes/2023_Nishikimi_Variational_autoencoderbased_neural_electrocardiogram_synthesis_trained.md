# Variational autoencoder–based neural electrocardiogram synthesis trained by FEM-based heart simulator
- **ID / Year / Venue:** P151 / 2023 / Cardiovascular Digital Health Journal
- **Model & task:** VAE (conditional VAE, fully connected encoder/decoder) trained on FEM simulator output (surrogate model); other (parameter-conditioned 12-lead ECG synthesis from 16 cardiac parameters; simulator surrogate)
- **Losses:** conditional VAE ELBO (reconstruction log-likelihood + KL divergence)
- **Evaluation:** Position Mean Absolute Error (PMAE) of Q, R, S, T fiducial positions vs ground truth; PSNR per lead; dependence of errors on cardiac parameter values (significance tests) (tags: fidelity;clinical;efficiency)
- **Data:** UT-Heart FEM multi-physics simulator dataset (2,880 ECG variations); leads: 12; fs: 500; length: 1 (single beat at 60 bpm, 500 samples)
- **Notes:** Paired evaluation against simulator ground truth; PSNR ~55-65 dB (very high because simulated noise-free signals). PMAE excludes P wave and outlier positions (>100/150 ms). Notes that appropriate metric depends on purpose (e.g. periodicity-focused for arrhythmia). Synthesis takes seconds on a laptop vs supercomputer hours.
- **Takeaway for ECGEN-Eval:** Fiducial-point position error (Q/R/S/T PMAE) is a clinically interpretable paired metric worth adding for conditional/paired tasks.
- *Extraction source: full-text*
