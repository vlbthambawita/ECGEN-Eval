# Implicit Neural Representations for ECG Synthesis: What is the Potential ?
- **ID / Year / Venue:** P091 / 2025 / IEEE/ACS International Conference on Computer Systems and Applications (AICCSA)
- **Model & task:** Diffusion (class-conditional DDPM, Attention U-Net) on implicit 2D representations (SDF / occupancy grids, wavelet coarse + detail predictor, INR feature planes + MLP decoder, marching squares); representation study vs explicit raw/spectrogram generators
- **Losses:** DDPM denoising loss; MSE for detail predictor; joint INR reconstruction
- **Evaluation:** qualitative visual inspection only; GPU memory/time per resolution [fidelity, efficiency]
- **Data:** MIT-BIH Arrhythmia; leads: 1; fs: not reported Hz; length: not reported s
- **Notes:** Negative result: SDF and INR diffusion failed to converge; occupancy grids noisy; no realistic ECGs produced. 1024x1024 grids cost ~12 GB and 3 h/epoch. No quantitative metrics for any method.
- **Takeaway for ECGEN-Eval:** Little to adopt metric-wise; it shows that generators which convert 2D/implicit representations back to 1D (marching squares) should be checked with ECGEN-Eval's signal-domain metrics (psd, sqi, heart_rate) rather than judged by images alone.
- *Extraction source: full-text*
