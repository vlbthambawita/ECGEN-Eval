# Reconstructing 12-lead ECG from 3-lead ECG using variational autoencoder to improve cardiac disease detection of wearable ECG devices

**Citation:** Guan X and Wang H and Lai Y and Jin J and Li J and Zhao Q and Zhang D and Geng S and Mu G and Wang Y and Wu R and Hong S. *Reconstructing 12-lead ECG from 3-lead ECG using variational autoencoder to improve cardiac disease detection of wearable ECG devices*. PLOS digital health, 2026. DOI: 10.1371/journal.pdig.0001335. arXiv: 2510.11442v1; first public: 2025-10-13; peer-reviewed date: 2026-05-22.

**Source/version:** [fulltext.xml](../papers/2026/Guan_2026_WearECG/fulltext.xml); [paper.pdf](../papers/2026/Guan_2026_WearECG/paper.pdf); [landing.html](../papers/2026/Guan_2026_WearECG/landing.html). [Landing page](https://doi.org/10.1371/journal.pdig.0001335).


**Task and model:** WearECG VAE reconstructs missing 12 leads from selected observed leads and evaluates reconstruction and physician reading; adjacent lead-translation included because it explicitly scores waveform generation.

**Data and split:** MIMIC 12-lead records;500Hz Fourier resampling, patient_id grouped split; main input leads II,V1,V5, compare I/II/V3 and single I. Exact record counts/signal length not in inspected sections.

**Evaluation metrics:** Paired MAE/MSE by lead; ECGFounder feature FID; 3 board-certified cardiologists blind Turing set50 mixed signals (52%,44%,44% correct); MI diagnosis on generated traces,55 cases: sensitivity100%,specificity44.8%,accuracy70.9%,F1 .765 (Results).

**Training objectives:** VAE ELBO Eq.8, MSE reconstruction + beta KL(q(z|x)||N(0,I)), beta=1e-4; latent channels4, AdamW,10epochs (Methods).

**Reported evidence:** Main leads II,V1,V5 overall MSE.00100, MAE.01782,FID12.64. Turing and MI confusion matrix as above.

**Clinical utility, experts and privacy:** Three experts assess realism and disease findings; MI assessment generated-only, specificity low; no utility vs paired real ECG or privacy attack.

**Reproducibility:** Published XML and PDF; subject split explicit; supplements/checkpoints not inspected.

**Critical assessment:** Reconstruction from partial observed leads relies on patient-specific paired signal, not population-level synthesis; near-chance detection does not validate safe diagnosis.
