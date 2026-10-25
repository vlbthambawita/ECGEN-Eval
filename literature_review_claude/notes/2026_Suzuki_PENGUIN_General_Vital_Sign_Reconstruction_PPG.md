# PENGUIN: General Vital Sign Reconstruction from PPG with Flow Matching State Space Model
- **ID / Year / Venue:** P112 / 2026 / arXiv
- **Model & task:** FlowMatching (OT-CFM with dual-stream S5 state-space Flow-SSM blocks; Heun sampler, 25 steps); PPG2ECG (also PPG->respiration, PPG->ABP)
- **Losses:** conditional flow matching loss (OT-CFM, L2 velocity regression)
- **Evaluation:** HR Error (MAE of heart rate in bpm, Hamilton detector, 8 s window); RR Error; SBP/DBP Error; qualitative waveform comparison; ablation (tags: clinical)
- **Data:** PPG-DaLiA; WildPPG (ECG); BIDMC; WESAD (resp); UCI-BP; MIMIC-BP (ABP); leads: 1; fs: 128 (resampled); length: not reported (metrics over 8 s windows)
- **Notes:** ECG reconstruction judged only by HR MAE (15.64 bpm DaLiA, 12.97 WildPPG) — no waveform-level metrics; cross-subject 6:1:1 split. Baselines: CycleGAN, RDDM, RespDiff, PaPaGei-S.
- **Takeaway for ECGEN-Eval:** Derived-physiology errors (HR MAE) are an easy clinical paired metric, but alone are insufficient for morphology.
- *Extraction source: full-text*
