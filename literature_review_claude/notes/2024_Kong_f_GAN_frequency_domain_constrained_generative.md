# f-GAN: A frequency-domain-constrained generative adversarial network for PPG to ECG synthesis
- **ID / Year / Venue:** P076 / 2024 / arXiv
- **Model & task:** f-GAN: frequency-constrained GAN translating wrist PPG to ECG
- **Losses:** Vanilla GAN + 0.1 * L1 on FFT magnitude spectra
- **Evaluation:** Heart-rate MAPE, peak-detection failure count, seed-level statistical testing
- **Data:** PPG-DaLiA, 128 Hz, 4 s/10 s segments, subject-disjoint
- **Takeaway for ECGEN-Eval:** Add peak-detection failure rate on synthetic ECGs and multi-seed statistical testing to ECGEN-Eval.
- *Extraction source: full-text*
