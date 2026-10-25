# Generating Precordial-lead Electrocardiogram from Smartwatch
- **ID / Year / Venue:** P079 / 2023 / Computing in cardiology
- **Model & task:** GAN (pix2pix-style U-Net generator, 5-layer conv discriminator; one model per precordial lead); task: lead-reconstruction
- **Losses:** not reported
- **Evaluation:** Fréchet distance (FD, per lead); MSE (per lead) (tags: fidelity; distribution)
- **Data:** Asan Medical Center 12-lead records (training); 10 healthy volunteers, Galaxy Watch4 + standard 12-lead (100 test recordings); leads: 1 -> 6 precordial (V1-V6); fs: 500 Hz; length: 2.5 segments stitched to 10 s
- **Notes:** Mean FD 15.46, MSE 0.0937; V1 best (FD 4.69), V3/V4 worst (~21). FD formula given as Gaussian Fréchet (mean+covariance), described as curve similarity — ambiguous. Very small real-world test set.
- **Takeaway for ECGEN-Eval:** Report per-lead FD; be explicit whether 'FD' is curve Fréchet or Gaussian Fréchet — literature conflates them.
- *Extraction source: full-text*
