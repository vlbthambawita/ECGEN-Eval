# Addressing Class Imbalance in ECG Arrhythmia Classification Using Latent Diffusion and Quantum-Enhanced Generative Modeling
- **ID / Year / Venue:** P011 / 2026 / AI in Medicine
- **Model & task:** Hybrid (spectral-guided cVAE + class-conditional latent DDPM + parameterized quantum circuit Quantum Latent Refinement); class-cond / augmentation
- **Losses:** unknown (abstract only); QLR module uses MMD minimization to align synthetic latents with real class-specific latent banks
- **Evaluation:** downstream 1D MobileNetV2 classification performance over 10 seeds and 4 augmentation ratios (specific metrics unknown) [utility-TSTR]
- **Data:** MIT-BIH Arrhythmia; leads: unknown (abstract only); fs: unknown (abstract only) Hz; length: unknown (abstract only; beat-level) s
- **Notes:** MMD used as a training objective in latent space rather than as eval metric. Quantum refiner comparable to classical latent diffusion. Multi-seed (10) evaluation of augmentation utility is good practice.
- **Takeaway for ECGEN-Eval:** Report augmentation utility across multiple seeds and augmentation ratios; latent MMD to class banks is a possible class-conditional fidelity check.
- *Extraction source: abstract-only*
