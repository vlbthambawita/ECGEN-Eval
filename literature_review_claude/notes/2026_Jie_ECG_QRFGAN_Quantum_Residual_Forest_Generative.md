# ECG-QRFGAN: A Quantum Residual Forest Generative Adversarial Network for Electrocardiogram Synthesis
- **ID / Year / Venue:** P064 / 2026 / International Conference on Biomedicine and Bioinformatics Engineering (ICBBE)
- **Model & task:** GAN (quantum: QResRNN generator + quantum random forest CNN discriminator, MPS/TTN circuits); class-cond / augmentation
- **Losses:** adversarial (details unknown, abstract only)
- **Evaluation:** Pearson correlation coefficient; PRD; RMSE; downstream classification accuracy; training convergence; robustness to quantum noise [fidelity; utility-TSTR; efficiency]
- **Data:** four public ECG repositories (unnamed in abstract); leads: unknown (abstract only); fs: unknown (abstract only) Hz; length: unknown (abstract only) s
- **Notes:** Uses paired-style metrics (PCC, PRD, RMSE) for unconditional-ish generation; unclear pairing protocol. Baselines BiGRU-CNN, ECG-QGAN, DCGAN.
- **Takeaway for ECGEN-Eval:** Classic PCC/PRD/RMSE triad persists; ECGEN-Eval should document nearest-neighbour pairing to make them meaningful for unpaired generation.
- *Extraction source: abstract-only*
