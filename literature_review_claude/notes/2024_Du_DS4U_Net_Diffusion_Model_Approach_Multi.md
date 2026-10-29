# DS4U-Net: A Diffusion Model-Based Approach to Multi-Lead ECG Signal Generation
- **ID / Year / Venue:** P054 / 2024 / International Conference on Intelligent Computing and Signal Processing (ICSP)
- **Model & task:** Diffusion (DDPM, T=200, S4 + 1D U-Net denoiser, network also used for learned forward noising); class-conditional 12-lead ECG generation for augmentation
- **Losses:** MSE noise-prediction loss
- **Evaluation:** visual inspection; MSE; RMSE; MAE; MAPE; DTW; Euclidean distance (leads I-III, 3000 random synthetic signals); SE-ResNet TSTR AUC/accuracy; ablations [fidelity, utility-TSTR]
- **Data:** PTB-XL; leads: 12; fs: not reported Hz; length: 10 s
- **Notes:** Lead I MSE 0.035 / DTW 47.6 vs best baseline 0.043 / 55.4; TSTR AUC 0.834, acc 0.878 vs Pulse2Pulse 0.791/0.802. Distance metrics are computed between randomly selected synthetic and real signals without a defined pairing, and the claimed spectral similarity is only visual.
- **Takeaway for ECGEN-Eval:** Illustrates the common misuse of paired metrics (MSE/DTW/ED) on unpaired class-conditional output; ECGEN-Eval's nearest-neighbour mae/dtw/prd and distributional psd should be documented as the correct replacements, with the pairing mode printed in the report.
- *Extraction source: full-text*
