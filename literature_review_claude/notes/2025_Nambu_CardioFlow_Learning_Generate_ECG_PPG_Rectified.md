# CardioFlow: Learning to Generate ECG from PPG with Rectified Flow
- **ID / Year / Venue:** P028 / 2025 / IEEE International Conference on Acoustics Speech and Signal Processing
- **Model & task:** FlowMatching (conditional rectified flow with RDDM-style velocity network, 1-50 Euler steps, probabilistic QRS/systolic-peak masks); PPG→ECG translation
- **Losses:** rectified-flow velocity regression on (optionally peak-masked) ECG conditioned on (masked) PPG
- **Evaluation:** RMSE; Fréchet distance; heart-rate MAE (Hamilton detector); sampling time vs steps; WESAD stress/emotion recognition Acc/F1; qualitative plots [fidelity, clinical, utility-TSTR, efficiency, conditional]
- **Data:** WESAD; PPG-DaLiA; leads: 1 (wearable ECG); fs: 128 Hz (resampled from 700); length: 4 s (concatenated to 8 s / 60 s)
- **Notes:** WESAD RMSE 0.24 / FD 10.4 / HR-MAE 5.1 bpm vs RDDM 0.21/7.2/6.9; DaLiA 0.22/8.8/7.5. Emotion recognition from generated ECG Acc 0.64 (real 0.66, PPG 0.55). Authors point out paired RMSE/FD favour damped QRS and penalise slight beat misalignment, while HR MAE rewards correct beat counts.
- **Takeaway for ECGEN-Eval:** For paired translation tasks, report a paired heart-rate/R-peak agreement metric (HR MAE from detected beats) next to RMSE/FD, and caveat that point-wise errors reward flattened QRS complexes.
- *Extraction source: full-text*
