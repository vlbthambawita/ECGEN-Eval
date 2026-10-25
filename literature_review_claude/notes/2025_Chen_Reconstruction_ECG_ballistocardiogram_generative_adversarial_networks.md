# Reconstruction of ECG from ballistocardiogram using generative adversarial networks with attention
- **ID / Year / Venue:** P125 / 2025 / Biomedical Physics & Engineering Express
- **Model & task:** GAN (Att-SNGAN: attention + spectral normalization); other-modality2ECG (BCG -> ECG)
- **Losses:** adversarial (SNGAN; other terms unknown, abstract only)
- **Evaluation:** MAE (0.0651); RMSE (0.0735); Fréchet Distance (0.0342); HRV analysis [fidelity; clinical]
- **Data:** in-house synchronous BCG (fiber optic) and ECG; leads: unknown (abstract only); fs: unknown (abstract only) Hz; length: unknown (abstract only) s
- **Notes:** 'Fréchet Distance' here is likely the discrete curve-matching distance, not FID-style; ambiguity in naming is a known pitfall.
- **Takeaway for ECGEN-Eval:** Disambiguate 'FD' (curve Fréchet vs Gaussian Fréchet) in ECGEN-Eval docs.
- *Extraction source: abstract-only*
