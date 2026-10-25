# PG-LRF: Physiology-Guided Latent Rectified Flow for Electro-Hemodynamic PPG-to-ECG Generation
- **ID / Year / Venue:** P114 / 2026 / arXiv
- **Model & task:** FlowMatching (latent rectified flow, PPG-conditioned, physiology-aware VAE-style autoencoder + electro-hemodynamic ODE simulator guidance); PPG2ECG
- **Losses:** PAE: phase-delay consistency (circular squared PAT distance) + L2 reconstruction + beta*KL + global posterior alignment + bidirectional InfoNCE contrastive (instance) + cross-modal decodability L2; Flow: rectified-flow velocity MSE + simulator-guided Euler residual losses on ECG and induced PPG; simulator fitting: waveform + derivative + peak-alignment losses
- **Evaluation:** MAE; RMSE; FD; FID; heart-rate MAE; fiducial MAE for PR, QRS, QT, QTcF, ST-J60 deviation, P-wave duration, T-wave duration (ms); downstream multi-label CVD detection AUROC (ICD I48, I71, I70, I44, I25, I50) and macro-AUROC; mean±SD over 3 runs [fidelity; distribution; clinical; utility-TSTR]
- **Data:** MC-MED (Stanford ED, 118,385 visits, 70,545 patients; official splits); leads: 1; fs: 120 (ECG; PPG 40 Hz) Hz; length: 10 s
- **Notes:** vs PPGFlowECG: MAE 0.87->0.71, FID 44.17->37.79, HR MAE 7.08->3.94; PR error 59.9 ms, QT 29.3 ms. Macro-AUROC 0.633 vs PPG baseline 0.545. Large interval errors even for SOTA show limits of PPG2ECG.
- **Takeaway for ECGEN-Eval:** Fiducial-interval MAE panel (PR, QRS, QT, QTcF, ST-J60, P, T durations) and HR MAE map directly to ECGEN-Eval features module.
- *Extraction source: full-text*
