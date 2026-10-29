# AI Generated Synthetic Electrocardiograms Demonstrate Morphological Preservation
- **ID / Year / Venue:** P014 / 2026 / Heart Lung and Circulation
- **Model & task:** GAN (WGAN-GP, EMA-averaged generator weights); class-specific synthesis of acute aortic dissection (AAD) ECGs for augmentation
- **Losses:** WGAN-GP (Wasserstein adversarial loss + gradient penalty)
- **Evaluation:** amplitude statistics (signal SD, peak-to-peak amplitude, global signal energy) with significance tests; PSD band comparison; DTW [fidelity, distribution]
- **Data:** MIMIC-IV-ECG (197 AAD ECGs augmented to 4,956; 60 held-out real for comparison); leads: not reported; fs: not reported Hz; length: not reported s
- **Notes:** Conference abstract only. Synthetic SD 17.1% lower, peak-to-peak +0.7%, energy 17.8% lower (p<0.001); PSD similar 5-150 Hz; DTW 1.30. Reduced variance and under-represented extreme values noted. No baseline, no real-real reference, no utility test, and pairing for DTW unspecified.
- **Takeaway for ECGEN-Eval:** Simple amplitude-distribution statistics (per-record SD, peak-to-peak, energy with effect sizes) detected variance shrinkage that DTW did not, so ECGEN-Eval should report such amplitude-spread summaries next to dtw/psd.
- *Extraction source: full-text*
