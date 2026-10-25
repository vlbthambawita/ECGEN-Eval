# One model, dual tasks: a novel distributionally adaptive learning framework for ECG classification and generation addressing intra- and inter-patient variability
- **ID / Year / Venue:** P109 / 2025 / Expert Systems with Applications
- **Model & task:** GAN (transformer generator + CNN discriminator, joint classifier, test-time adaptation); class-cond / augmentation
- **Losses:** adversarial + classification (details unknown, abstract only)
- **Evaluation:** classification performance under intra- and inter-patient paradigms (specific metrics unknown) [utility-TSTR]
- **Data:** MIT-BIH Arrhythmia; MIT-BIH Supraventricular; INCART; leads: unknown (abstract only); fs: unknown (abstract only) Hz; length: single heartbeat s
- **Notes:** Generation evaluated only through downstream inter-patient classification, per abstract.
- **Takeaway for ECGEN-Eval:** Inter-patient split matters for utility evaluation; ECGEN-Eval utility tests should respect patient-wise splits.
- *Extraction source: abstract-only*
