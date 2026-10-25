# Generative adversarial networks (GANs) to produce synthetic 12-lead electrocardiogram signals for specific and rare diseases: a novel, powerful tool towards clinical advancements
- **ID / Year / Venue:** P084 / 2024 / European Heart Journal
- **Model & task:** GAN (general GAN + DeceptionECG, InceptionTime-inspired GAN); class-cond (disease-specific)
- **Losses:** unknown (abstract only)
- **Evaluation:** independent discriminator DL model accuracy (real vs fake); cardiologist real-vs-synthetic discrimination accuracy (Turing test); disease-classifier accuracy on synthetic (TRTS-like); augmentation accuracy on real test set (tags: expert;utility-TSTR;fidelity)
- **Data:** PTB-XL; leads: 12; fs: unknown (abstract only); length: unknown (abstract only)
- **Notes:** Anterior STEMI: discriminator ACC 48.9%, clinicians 56%/51% (chance-level); TRTS ACC 88.7%; augmentation 94.6% vs 89.3%. 2,500 12-lead ECGs/min.
- **Takeaway for ECGEN-Eval:** Post-hoc real-vs-fake classifier accuracy (C2ST, ~50% ideal) is a cheap metric worth adding.
- *Extraction source: abstract-only*
