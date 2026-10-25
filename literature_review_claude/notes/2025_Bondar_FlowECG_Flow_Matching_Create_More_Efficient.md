# FlowECG: Using Flow Matching to Create a More Efficient ECG Signal Generator
- **ID / Year / Venue:** P077 / 2025 / arXiv
- **Model & task:** FlowMatching (rectified/linear-path flow matching on SSSD-ECG S4 backbone); class-cond (71 PTB-XL diagnostic statements)
- **Losses:** Flow matching L2 velocity regression ||f(x_t,c,t)-(x1-x0)||^2 (baseline SSSD-ECG: diffusion MSE noise prediction)
- **Evaluation:** DTW; 1-Wasserstein distance on handcrafted statistical/temporal/spectral features; MMD; spectral similarity score 1/(1+mean W(PSD_real,PSD_gen)); NFE vs quality curves; all per-lead averaged [fidelity; distribution; efficiency]
- **Data:** PTB-XL; leads: 12 (8 generated: I, aVF, V1-V6; remaining 4 derived); fs: 100 (1000 timesteps for 10 s) Hz; length: 10 s
- **Notes:** At 200 NFE: MMD 21.09 vs 80.70 (SSSD-ECG), DTW 83.96 vs 73.49, W 0.62 vs 1.03, SimScore 0.37 vs 0.30. Comparable quality at 10-25 NFE. Explicitly notes field lacks standardized protocols. No utility or clinical metrics.
- **Takeaway for ECGEN-Eval:** Quality-vs-NFE (sampling budget) curves and PSD-Wasserstein spectral similarity are worth adding; ECGEN-Eval already has DTW/MMD/PSD.
- *Extraction source: full-text*
