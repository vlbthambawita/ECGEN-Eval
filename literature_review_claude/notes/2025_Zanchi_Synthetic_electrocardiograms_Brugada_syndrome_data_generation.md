# Synthetic electrocardiograms for Brugada syndrome: from data generation to expert cardiologists evaluation
- **ID / Year / Venue:** P143 / 2025 / European Heart Journal - Digital Health
- **Model & task:** GAN (Pulse2Pulse); task: evaluation (expert Turing test of class-specific synthetic ECGs)
- **Losses:** not reported (refers to Pulse2Pulse paper)
- **Evaluation:** Expert visual Turing test by 7 Brugada specialists (>15 y): accuracy, sensitivity, specificity, precision, F1 (real=positive); two rounds ≥2 h apart; Wilcoxon signed-rank; intra-rater Cohen's kappa (tags: expert)
- **Data:** Private: 12-lead ECGs from 21 Brugada syndrome patients (5-min recordings); leads: 12; fs: 1000 Hz; length: 10 (1122 real + 1122 synthetic instances) s
- **Notes:** Experts at chance or worse: accuracy 40%/42%, specificity 22%/26%, sensitivity 58%; kappa −0.12 to 0.80. Bias toward calling ECGs real. Same display settings (25 mm/s, 10 mm/mV). Raises disclosure/watermarking concerns.
- **Takeaway for ECGEN-Eval:** Expert Turing-test protocol (blinded, repeated rounds, kappa) is a template; report specificity separately since raters are biased to 'real'.
- *Extraction source: full-text*
