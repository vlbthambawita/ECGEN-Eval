# Biomedically Informed ECG Synthesis: Customizing Cardiac Cycle Phases with Diffusion Model
- **ID / Year / Venue:** P157 / 2024 / IEEE International Conference on Bioinformatics and Biomedicine (BIBM)
- **Model & task:** DIFF-ECG: DiffWave-style diffusion with Semantic ECG Batch Normalization (SPADE-like) blocks; generates ECG that follows a P/QRS/T location mask
- **Losses:** DDPM epsilon-MSE
- **Evaluation:** segmentation-based adherence (real-trained segmenter on generated ECG, onset/offset recall/precision at 150 ms tolerance) and train-on-synthetic segmenter tested on real ECG; real reference row [conditional, clinical, utility-TSTR]
- **Data:** QT Database (105 two-channel Holter records, expert wave annotations); leads: not reported; fs: 125 Hz; length: 4 s
- **Notes:** Generated-signal segmentation onset R/P 91.37/94.04 vs SSSD-ECG 90.34/89.07 and real 98.34/97.12; synthetic-trained segmenter on real 97.03/96.87. No distribution, diversity, morphology-amplitude or privacy evaluation; 150 ms tolerance is wide for P/QRS boundaries and timing errors are not reported.
- **Takeaway for ECGEN-Eval:** For mask/fiducial-conditioned generators, ECGEN-Eval's delineation module could report onset/offset detection recall/precision and mean timing error of generated vs requested P/QRS/T boundaries, with tighter tolerances than the AAMI 150 ms used here.
- *Extraction source: full-text*
