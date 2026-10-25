# Style translation of simulated ECGs to realistic ECGs with generative adversarial networks for data-scarce clinical settings: challenges and opportunities
- **ID / Year / Venue:** P135 / 2026 / European Heart Journal - Digital Health
- **Model & task:** GAN (CycleGAN style transfer simulated->realistic ECG); task: other (simulation-to-real style translation / augmentation)
- **Losses:** CycleGAN adversarial + cycle-consistency (implied by CycleGAN; not detailed)
- **Evaluation:** Downstream RBBB classifier AUC; average precision (AP) for real-only, real+raw simulations, real+translated simulations (tags: utility-TSTR)
- **Data:** PTB-XL (987 ECGs, 56 RBBB); MedalCareXL simulations (25 RBBB); leads: not reported; fs: not reported Hz; length: not reported s
- **Notes:** Conference abstract. Raw simulations harmed (AUC 0.93, AP 0.68); translated restored to baseline (AUC 0.95 vs 0.96, AP 0.81 vs 0.79). Notes clinicians recognise synthetic style; argues diffusion models offer objective convergence diagnostics vs unstable GANs.
- **Takeaway for ECGEN-Eval:** Report the 'harm' case: augmentation can degrade utility; include real-only baseline and AP for rare classes.
- *Extraction source: full-text*
