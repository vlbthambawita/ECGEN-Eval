# DeepFake electrocardiograms using generative adversarial networks are the beginning of the end for privacy issues in medicine
- **ID / Year / Venue:** P166 / 2021 / Scientific Reports
- **Model & task:** GAN (WaveGAN* and Pulse2Pulse U-Net generator, WGAN-GP); task: unconditional
- **Losses:** WGAN-GP (gradient penalty), 5 critic updates per generator update
- **Evaluation:** Fraction of synthetic ECGs classified 'Normal' by commercial GE MUSE 12SL algorithm (model selection across epochs); distributions of MUSE-measured HR, P duration, QT, QRS, PR, STJ/R/T amplitudes vs real; QT-RR correlation preservation; covariance structures (tags: clinical; distribution)
- **Data:** GESUS; Inter99 (Danish population studies; MUSE 12SL 'Normal' ECGs only); leads: 8 independent (I, II, V1-V6) -> 12 derived; fs: 500 Hz; length: 10 s
- **Notes:** 150,000 DeepFake ECGs released; 81.3% classified Normal. Clinical-parameter distributions matched; truncation of HR at clinical boundaries discussed. Privacy claimed but not quantitatively tested (no memorization/MIA).
- **Takeaway for ECGEN-Eval:** Use an external ECG interpretation program as an oracle: % plausible/diagnosis-consistent plus clinical-parameter distribution and covariance (e.g., QT-RR) comparison.
- *Extraction source: full-text*
