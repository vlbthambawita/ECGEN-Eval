# PPG-to-ECG Signal Translation for Continuous Atrial Fibrillation Detection via Attention-based Deep State-Space Modeling
- **ID / Year / Venue:** P117 / 2024 / n/a
- **Model & task:** SSM (attention-based deep state-space model, conditional variational / deep Kalman-style latent model); task: PPG2ECG
- **Losses:** Conditional variational lower bound (ELBO): emission reconstruction log-likelihood − β·KL(posterior || PPG-conditioned prior) at each timestep
- **Evaluation:** Pearson correlation; RMSE (mV); SNR (dB); AF detection ROC-AUC, PR-AUC, F1 (MINA classifier trained on real ECG, tested on translated) (tags: fidelity; utility-TSTR)
- **Data:** MIMIC-III Waveform Matched Subset (55 subjects: 43 healthy, 12 AF); leads: 1; fs: 125 Hz; length: 4 (beat-wise, PP interval interpolated to 90 samples) s
- **Notes:** ρ 0.858/RMSE 0.07/SNR 15.4 dB clean; 0.847/0.076/13.9 under baseline+Gaussian noise. AF PR-AUC 0.986 vs 0.987 real. Probabilistic model provides uncertainty bands for translated ECG.
- **Takeaway for ECGEN-Eval:** Robustness-to-input-noise evaluation and uncertainty for paired translation; train-on-real/test-on-synthetic for classifier compatibility.
- *Extraction source: full-text*
