# A GENERATIVE MODEL FOR DEEP FAKE AUGMENTATION OF PHONOCARDIOGRAM AND ELECTROCARDIOGRAM SIGNALS USING LSGAN AND CYCLE GAN
- **ID / Year / Venue:** P003 / 2023 / Informatyka Automatyka Pomiary w Gospodarce i Ochronie Środowiska
- **Model & task:** GAN (LSGAN; CycleGAN); augmentation (class balancing; ECG and PCG)
- **Losses:** Least-squares adversarial loss (LSGAN); CycleGAN adversarial + cycle-consistency loss
- **Evaluation:** MSE; SSIM; PSNR (defined, not tabulated); cross-correlation coefficient (defined); VGG-16 arrhythmia classification accuracy, precision, recall, F1 [fidelity; utility-TSTR]
- **Data:** MIT-BIH Arrhythmia; PTB Diagnostic (stated); PCG: PASCAL Heart Sound Challenge, PhysioNet CinC 2016, Michigan Heart Sound and Murmur Library; leads: not reported; fs: not reported (PTB described as 1000 Hz) Hz; length: not reported s
- **Notes:** CycleGAN ECG: MSE 0.0651, SSIM 0.9823; classifier F1 0.9035. Reported numbers inconsistent between abstract/table and conclusion (F1 90.35% vs 97.22%). Image metrics (SSIM, PSNR) applied to 1-D signals; pairing protocol for MSE/SSIM not described.
- **Takeaway for ECGEN-Eval:** Weak evaluation example: image metrics on 1-D signals without stated pairing; ECGEN-Eval should state pairing (nearest neighbour) explicitly.
- *Extraction source: full-text*
