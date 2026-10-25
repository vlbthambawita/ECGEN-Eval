# Evaluating the Quality of CycleGAN Generated ECG Data for Myocardial Infarction Classification
- **ID / Year / Venue:** P073 / 2024 / Computing in cardiology
- **Model & task:** GAN (CycleGAN style transfer, 2 CycleGANs / 4 generators); other (style transfer NORM<->ASMI/IMI heartbeats; augmentation)
- **Losses:** CycleGAN losses (adversarial + cycle consistency, as in Zhu et al.; not detailed)
- **Evaluation:** 95% confidence-band plots per lead; UMAP 2D density/scatter (fit on real); GAN-train score; GAN-test score (vs baselines); ST-segment amplitude comparison via modified Hotelling T² simultaneous 95% intervals per lead (tags: distribution;utility-TSTR;clinical)
- **Data:** PTB-XL (10,776 ECGs: NORM, ASMI, IMI); leads: 12; fs: 100; length: 0.40 (single beat window, -100 to +300 ms)
- **Notes:** Negative result: GAN-train 62% vs baseline 98%; GAN-test 81% vs baseline 89%; ST amplitudes significantly different in all conditions; distributions overlapped only in tails. Warns image-domain GANs cannot simply be adapted to ECG.
- **Takeaway for ECGEN-Eval:** Add GAN-train/GAN-test with baselines and per-lead ST-amplitude Hotelling-style intervals; confidence-band plots are a cheap visual diagnostic.
- *Extraction source: full-text*
