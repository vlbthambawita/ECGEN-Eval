# Generating Time Series Data With Real-Valued DC-GAN From Complex Time-Frequency Domain: Application to ECG Synthesis
- **ID / Year / Venue:** P081 / 2024 / IEEE Access
- **Model & task:** GAN (2-D real-valued DC-GAN on real/imaginary STFT coefficients packed in RGB channels, inverse STFT to waveform); class-wise synthesis of N/V/F beats and 5 s AF and VT strips (one GAN per class)
- **Losses:** standard DC-GAN adversarial loss
- **Evaluation:** MSE, RMSE, DTW between generated samples and visually matched originals; visual inspection [fidelity]
- **Data:** MIT-BIH Arrhythmia (MLII); MIT-BIH AF; MIT-BIH Malignant Ventricular Ectopy; leads: 1; fs: 360 (beats) / 250 (AF, VT) Hz; length: 0.75 (beats) / 5 (AF, VT) s
- **Notes:** Beat MSE ~1e-7; AF RMSE 6.86e-4, DTW 24.3; VT RMSE 7.80e-4, DTW 59.6. All numbers come from a few generated samples paired with hand-picked similar originals; there is no distributional, diversity, downstream or memorisation evaluation.
- **Takeaway for ECGEN-Eval:** A cautionary example of cherry-picked pairing; ECGEN-Eval's nearest-neighbour mae/dtw should be computed over the full synthetic set and always reported next to nn_dist so near-zero errors are flagged as possible memorisation.
- *Extraction source: full-text*
