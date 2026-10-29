# Synthesis of Standard 12-Lead ECG from Single-Lead ECG Using Shifted Diffusion Models
- **ID / Year / Venue:** P163 / 2024 / Lecture notes in computer science (ECML PKDD 2024, LNAI 14949)
- **Model & task:** SD-ECG: shifted diffusion in the STFT time-frequency domain whose forward process drifts toward a learned, lead-I-conditioned shift (with age/sex); Transformer denoiser with lead-correlation cross-attention; lead I -> remaining 11 leads
- **Losses:** simplified x0-prediction L2 loss (unweighted) with jointly trained shift network
- **Evaluation:** per-lead MSE and discrete Fréchet distance vs ground truth; MIT-BIH classifier ROC-AUC on synthesized leads; ablation; diffusion-step sensitivity; case study [fidelity, utility-TSTR, conditional]
- **Data:** PTB-XL (train/test), Tianchi and MIT-BIH (zero-shot); leads: 12 (11 generated); fs: 125 Hz; length: 10 s
- **Notes:** PTB-XL average MSE 0.0117 / FD 2.587 vs Nef-Net 0.0184 / 5.074; best on 10 of 11 leads; MIT-BIH ROC-AUC SVEB 0.802, Fusion 0.866. 'MSE' is defined with an absolute value; a single sample per input is evaluated, so the stochastic model's spread is not assessed.
- **Takeaway for ECGEN-Eval:** For lead-reconstruction tasks ECGEN-Eval should support a paired mode that reports per-lead MSE/MAE and curve Fréchet distance against ground-truth leads, and should document metric formulas exactly, since this paper's 'MSE' is actually an absolute error.
- *Extraction source: full-text*
