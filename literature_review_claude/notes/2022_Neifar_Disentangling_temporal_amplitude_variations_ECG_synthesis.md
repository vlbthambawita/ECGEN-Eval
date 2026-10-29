# Disentangling temporal and amplitude variations in ECG synthesis using anchored GANs
- **ID / Year / Venue:** P176 / 2022 / ACM SAC 2022
- **Model & task:** Anchored GAN: per-class K-means anchor beats; generator outputs an amplitude offset s and a sparse monotonic warping matrix W so that X = W(A + s); class-conditional (N, V, F) MIT-BIH beat synthesis for augmentation
- **Losses:** Standard GAN BCE + l1−l2 sparsity loss on W
- **Evaluation:** Visual comparison; per-class precision/recall/F1 of three beat classifiers trained with real, real+standard-GAN and real+anchored-GAN data [utility-TSTR]
- **Data:** MIT-BIH Arrhythmia; leads: single channel; fs: 360 Hz; length: 0.75 s beats (270 samples)
- **Notes:** Fusion-class F1 improves 0.81→0.90 (vs 0.85 with standard GAN); N/V unchanged at ~0.99. No signal-level or distributional metrics; synthetic beats visibly noisier than real; augmentation sizes not reported.
- **Takeaway for ECGEN-Eval:** Beat-level generators that are judged only by augmentation F1 leave fidelity untested, so ECGEN-Eval should let users run its distribution metrics (mmd, fd, prd nearest-neighbour, psd) per class on R-aligned beats and add a per-class breakdown to the report.
- *Extraction source: full-text*
