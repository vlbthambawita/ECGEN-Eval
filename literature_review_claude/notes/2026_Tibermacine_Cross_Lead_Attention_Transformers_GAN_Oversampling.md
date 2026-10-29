# Cross-Lead Attention Transformers with GAN Oversampling for Robust ECG Arrhythmia Detection
- **ID / Year / Venue:** P040 / 2026 / Electronics
- **Model & task:** GAN (standard vanilla GAN, BCE loss, latent 100) generating minority-class beats for oversampling; per-lead CNN + cross-lead Transformer classifier; class-conditional augmentation
- **Losses:** standard minimax GAN binary cross-entropy
- **Evaluation:** DTW; Pearson correlation; MMD; SNR; intra-class variance ratio; blinded expert identification (2 cardiologists, 200+200 beats); diagnostic consistency; plausibility score; rare-class F1 augmentation gain; classifier efficiency [fidelity, distribution, diversity, expert, utility-TSTR, efficiency]
- **Data:** MIT-BIH Arrhythmia (16 classes, patient-level split); external ECG5000, INCART; leads: 2 (MIT-BIH; generated lead count unclear); fs: 360 Hz; length: 0.36 s beats
- **Notes:** 5,000 synthetic beats: DTW 0.31, r 0.84, MMD 0.042, SNR 23.7 dB, variance ratio 0.88-1.12; experts identify synthetic at 47.8% (chance), diagnostic consistency 91.5%, plausibility 4.1/5; augmentation +0.8-1.5 F1 pts. Pairing for DTW/correlation and MMD feature space are unspecified; ablation numbers (macro F1 94.75% without augmentation) conflict with the augmentation table (+1.2 pts).
- **Takeaway for ECGEN-Eval:** Good template for a multi-angle report (similarity + variance-ratio diversity + expert + utility); ECGEN-Eval should add a per-class synthetic/real variance-ratio diversity metric and require explicit pairing and kernel/feature documentation for DTW/correlation/MMD so such numbers are reproducible.
- *Extraction source: full-text*
