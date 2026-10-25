# Generative Reconstruction of Multimodal Cardiac Waveforms From a Single Vibrational Cardiography Sensor
- **ID / Year / Venue:** P087 / 2025 / IEEE journal of biomedical and health informatics
- **Model & task:** GAN (conditional); other-modality2ECG (vibrational cardiography -> ECG, ICG, NIBP, PPG)
- **Losses:** conditional adversarial (details unknown, abstract only)
- **Evaluation:** Pearson correlation coefficient (median ECG 0.808); fiducial point analysis; leave-one-subject-out validation; per-intervention consistency [fidelity; clinical]
- **Data:** in-house: 20 subjects, VCG at xiphoid with ECG/ICG/NIBP/PPG; breath-hold, deep breathing, cold pressor; leads: unknown (abstract only); fs: unknown (abstract only) Hz; length: unknown (abstract only) s
- **Notes:** LOSO protocol for calibration-free generalization; fiducial point timing analysis as clinical check.
- **Takeaway for ECGEN-Eval:** Fiducial-point timing errors (R, Q, S, T locations) are a useful paired clinical metric.
- *Extraction source: abstract-only*
