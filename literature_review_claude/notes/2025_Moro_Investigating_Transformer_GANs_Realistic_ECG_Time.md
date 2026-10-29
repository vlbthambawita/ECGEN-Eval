# Investigating Transformer-Based GANs for Realistic ECG Time-Series Data Generation
- **ID / Year / Venue:** P096 / 2025 / IEEE International Symposium on Computer-Based Medical Systems (CBMS)
- **Model & task:** GAN (TTS-CGAN, Transformer encoders in G and ViT-style D with class head); class-conditional MIT-BIH heartbeat generation plus MIMIC-IV hourly heart-rate trend generation; retraining the GAN on hybrid real/synthetic mixtures
- **Losses:** LSGAN loss + discriminator class head; DiffAug, EMA
- **Evaluation:** example-pair DTW; PCA/t-SNE; per-class cosine similarity and JS distance; heatmaps; hybrid-retraining comparison [fidelity, distribution]
- **Data:** MIT-BIH Arrhythmia (187-sample pre-processed beats, 5 classes); MIMIC-IV charted heart rate (not ECG); leads: 1; fs: not reported Hz; length: not reported (187 samples) s
- **Notes:** Cosine 0.84-0.99, JS 0.12-0.24, DTW 0.10-0.26. The abstract's 'classification performance on hybrid datasets' is actually the GAN retrained on mixed data and re-scored with cosine/JS; no classifier or TSTR is run. Half the study models hourly heart-rate values rather than ECG waveforms.
- **Takeaway for ECGEN-Eval:** Mean cosine similarity and value-histogram JS saturate near 1/0 on normalised beats; ECGEN-Eval should prefer embedding/feature-level distribution metrics (fd, mmd, pr_dist) and document that per-sample cosine on min-max normalised beats is not discriminative.
- *Extraction source: full-text*
