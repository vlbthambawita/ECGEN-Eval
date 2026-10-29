# Generative adversarial networks (GANs) to produce synthetic 12-lead electrocardiogram signals for specific and rare diseases: a novel, powerful tool towards clinical advancements
- **ID / Year / Venue:** P084 / 2024 / European Heart Journal (Suppl 1, ESC Congress abstract)
- **Model & task:** GAN (general GAN on PTB-XL feeding DeceptionECG, an InceptionTime-inspired disease-specific GAN); class-conditional 12-lead synthesis for AF, anterior STEMI, WPW and others
- **Losses:** not reported
- **Evaluation:** DL real-vs-fake discriminator; two-cardiologist Turing test; TRTS disease recognition; augmentation gain; generation speed [fidelity, expert, utility-TSTR, conditional, efficiency]
- **Data:** PTB-XL (>21,000 ECGs); leads: 12; fs: not reported Hz; length: not reported s
- **Notes:** Anterior STEMI: discriminator 48.9%, clinicians 56%/51%; TRTS 88.7%; augmentation 94.6% vs 89.3%; 2,500 ECGs/min. The PDF is a one-page congress abstract (plus figure captions), so architectures, sample sizes per test and statistics are missing.
- **Takeaway for ECGEN-Eval:** Supports adding a classifier two-sample test (real-vs-synthetic accuracy near 50%) and a label-adherence check with a pre-trained disease classifier to the report, with sample sizes and confidence intervals that this abstract lacks.
- *Extraction source: full-text*
