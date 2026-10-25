# Deep conditional generative model for personalization of 12-lead electrocardiograms and cardiovascular risk prediction

**Citation:** Sang Y and Banerjee A and Beetz M and Grau V. *Deep conditional generative model for personalization of 12-lead electrocardiograms and cardiovascular risk prediction*. Frontiers in digital health, 2025. DOI: 10.3389/fdgth.2025.1558589. arXiv: not applicable; first public: 2025-04-16; peer-reviewed date: 2025-04-16.

**Source/version:** [fulltext.xml](../papers/2025/Sang_2025_Personalization/fulltext.xml). [Landing page](https://doi.org/10.3389/fdgth.2025.1558589).


**Task and model:** Conditional VAE generates subject-specific 12-lead ECG from anatomy/demographics/electrode positions; explicitly generates samples and evaluates morphology against in-silico simulation (Methods §2.5; Results §§3.1–3.2).

**Data and split:** UK Biobank 37,508 participants; 10-s,500Hz,12 leads; 21,083 paired ECG/MRI cases for anatomy experiments. Each VAE 80/20 train/test, batch64,80 epochs; split unit called dataset and subject-disjointness unclear. Median beats used in most analyses. Separate incident-CVD cohort 33,713 subjects.

**Evaluation metrics:** Morphological trends by lead under heart translation/rotation compared qualitatively with mechanistic simulation; only partial lead-wise agreement and some directional disagreements (§§3.1–3.2). Incident risk C-index .63; +sex/age .65 (§3.3), separate risk model, not generation fidelity. No scalar FID, expert, privacy or TSTR.

**Training objectives:** Conditional ELBO Eq.14: negative expected log-likelihood represented by waveform MSE plus beta KL(q(z|x,y)||N(0,I)); beta example 1e-4. Anatomy condition concatenated into encoder and decoder; random latent samples generate signal (Methods §2.5).

**Reported evidence:** Anatomical rotation/translation trends compared against Mincholé simulation; agreement varies by lead and some trends are opposite (Results §§3.1–3.2). C-index is not a generative quality score. No multi-run uncertainty.

**Clinical utility, experts and privacy:** No held-out generation metric or independent clinicians; no TSTR or MIA. 1,834 electrode-position subset; generative model split protocol underspecified.

**Reproducibility:** Peer-reviewed Frontiers Digital Health full text and architecture available. ELBO and MRI subset count reported; beta setting example only.

**Critical assessment:** Comparison tests anatomy-conditioned trends rather than population distributions. Incomplete and opposite lead trends qualify physiological-consistency claims.
