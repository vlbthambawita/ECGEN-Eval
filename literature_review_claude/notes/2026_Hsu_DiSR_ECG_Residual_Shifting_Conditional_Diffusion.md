# DiSR-ECG: Residual Shifting Conditional Diffusion for Robust ECG Super-Resolution
- **ID / Year / Venue:** P053 / 2026 / arXiv
- **Model & task:** Diffusion (residual-shifting conditional diffusion, ResShift-style, Mamba temporal backbone; DiSR-ECG); super-resolution (50 Hz -> 500 Hz, with noise robustness)
- **Losses:** L1 reconstruction + scale-invariant SDR (negative SI-SDR, lambda_SI=0.02)
- **Evaluation:** MSE; Cosine Similarity (CoS); SNR (dB); Maximum Absolute Deviation (MAD); paired-sample t-test significance
- **Data:** PTB-XL (train/in-domain); Chapman-Shaoxing (zero-shot cross-dataset); MIT-BIH Noise Stress Test DB (noise injection); leads: 12; fs: 500 (target); 50 (low-res input); length: 10
- **Takeaway for ECGEN-Eval:** Add SI-SDR / cosine similarity / max-abs-deviation for paired tasks, plus paired significance tests.
- *Extraction source: full-text*
