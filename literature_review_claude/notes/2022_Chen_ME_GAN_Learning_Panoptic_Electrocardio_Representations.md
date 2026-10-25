# ME-GAN: Learning Panoptic Electrocardio Representations for Multi-view ECG Synthesis Conditioned on Heart Diseases
- **ID / Year / Venue:** P169 / 2022 / arXiv (Cornell University)
- **Model & task:** GAN (ME-GAN: two-stage generator with Nef-Net decoder, MixNorm disease conditioning; LSGAN + ACGAN-style major discriminator + view discriminator); class-cond (heart disease-conditioned multi-view/12-lead ECG synthesis)
- **Losses:** LSGAN least-squares adversarial loss (a=1, b=0) + auxiliary disease classification CE/BCE (ACGAN-style) + view-discriminator MSE angle-regression adversarial loss (view-consistency)
- **Evaluation:** relative FID (rFID = FID(gen, X2)/FID(X1, X2), real-real split as normaliser); 1-NN classifier accuracy (1NNC two-sample test); augmentation PR-AUC with 1D ResNet-34; pairwise distance among views within same case vs real baseline; rFID sensitivity to noise/line-segment/blur perturbations (tags: distribution;utility-TSTR;fidelity)
- **Data:** Tianchi ECG (31,779 records, 500 Hz; LAD, RAD, RBBB); PTB (549 records, 1000 Hz); leads: 12 (multi-view, arbitrary angles via Nef-Net); fs: 500 (Tianchi); 1000 (PTB); length: single cardiac cycle (512 samples)
- **Notes:** Proposes rFID to normalise image-pretrained-feature FID by a real-vs-real FID; validated monotone response to noise, blur, line-segment perturbations; real-real denominator std 0.212 on PTB. Baseline augmentation PR-AUC 0.879. Feature extractor not ECG-trained — a known weakness later addressed by ECG foundation-model FED.
- **Takeaway for ECGEN-Eval:** Report FD/FED alongside a real-vs-real reference (ratio, as in rFID) and add 1-NN two-sample accuracy; view/lead-consistency distance is a useful multi-lead metric.
- *Extraction source: full-text*
