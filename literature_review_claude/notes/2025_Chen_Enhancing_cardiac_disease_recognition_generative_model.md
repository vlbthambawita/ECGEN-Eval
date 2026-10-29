# Enhancing cardiac disease recognition with generative model-based data augmentation
- **ID / Year / Venue:** P070 / 2025 / IET conference proceedings (ICASI 2025)
- **Model & task:** Diffusion (DDPM, 200 steps; DeScoD-ECG-based backbone with enhanced half-normalized filters, modified ELAN, multi-scale convs, time-adaptive weighting; CLIP text-encoder conditioning); text-conditional augmentation of PTB-XL hypertrophy
- **Losses:** not reported explicitly (standard DDPM denoising objective implied)
- **Evaluation:** per-class and mean AUC of InceptionTime trained with vs without synthetic augmentation; architecture ablations [utility-TSTR]
- **Data:** PTB-XL; leads: 12 (8 generated, 4 derived); fs: not reported Hz; length: 10 s
- **Notes:** Mean AUC 92.45 -> 93.20% with 2,000 synthetic HYP ECGs (MI AUC +2.1). No fidelity, distribution or clinical metrics at all; single runs without variance; the sub-1% gain is not significance-tested.
- **Takeaway for ECGEN-Eval:** Typical utility-only paper; ECGEN-Eval reports should pair any augmentation-AUC claim with distribution metrics (fed/mmd) and class-conditional clinical-feature checks, and encourage repeated-seed confidence intervals for small AUC gains.
- *Extraction source: full-text*
