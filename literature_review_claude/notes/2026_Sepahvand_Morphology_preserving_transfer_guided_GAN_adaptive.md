# Morphology-preserving transfer-guided GAN with adaptive discriminative loss for robust and imbalanced ECG arrhythmia detection
- **ID / Year / Venue:** P106 / 2026 / Computers in biology and medicine
- **Model & task:** GAN (Transfer-Guided Multi-Stage GAN, TG-MS-GAN); augmentation (class-cond minority beats)
- **Losses:** GAN loss unknown; classifier adaptive hybrid loss: weighted cross-entropy + center loss + difficulty-based focusing
- **Evaluation:** classification accuracy; Macro-F1; AUPRC (tags: utility-TSTR)
- **Data:** MIT-BIH; Chapman-Shaoxing; PTB-XL; Fetal ECG; leads: unknown (abstract only); fs: unknown (abstract only); length: beat
- **Notes:** Claims preservation of P-wave, QRS, ST morphology but abstract reports only downstream classifier metrics (acc 99.1/97.6/91.4/99.0%).
- **Takeaway for ECGEN-Eval:** Illustrates the common gap: morphology claims without direct morphology metrics — clinical feature metrics needed.
- *Extraction source: abstract-only*
