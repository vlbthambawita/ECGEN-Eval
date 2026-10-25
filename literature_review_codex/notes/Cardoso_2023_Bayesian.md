# Bayesian ECG reconstruction using denoising diffusion generative models

**Citation:** Gabriel V. Cardoso and Lisa Bedin and Josselin Duchateau and Rémi Dubois and Eric Moulines. *Bayesian ECG reconstruction using denoising diffusion generative models*. arXiv, 2023. DOI: not identified. arXiv: 2401.05388v1; first public: 2023-12-18; peer-reviewed date: not verified.

**Source/version:** [paper.pdf](../papers/2023/Cardoso_2023_Bayesian/paper.pdf); [landing.html](../papers/2023/Cardoso_2023_Bayesian/landing.html). [Landing page](https://arxiv.org/abs/2401.05388v1).


**Task and model:** ECGDiff conditional variance-exploding denoising diffusion for healthy beats; age/sex/RR conditioning, then Bayesian SMC posterior sampling for reconstruction and anomaly detection. Included because unconditional/conditional prior generation is explicitly evaluated (§2.6).

**Data and split:** PhysioNet2021: 43,101 records; normal beats from28,167 patients and MI468. Nine channels aVL/aVR/aVF/V1–V6,250Hz,176samples (704ms) around R peak; each lead divided by QRS maximum absolute amplitude. Generation evaluation samples one beat/patient;22580 training patients,2864 test; CV remainder reported separately (pp.4–6).

**Evaluation metrics:** Generation: EMD optimal transport on concatenated waveform and conditioning attributes, equal2864-sized real/generated sets, training batches and real-real/noisy-real references; lower. Random-network distillation support-uncertainty: mean squared representation mismatch across10 bootstrap network pairs,1024D,20epochs; lower not automatically better than real reference. Reconstruction R² ↑ and rescaled Mahalanobis distance; QT–RR physiology curves,95%CLT intervals; MI ROC/AUC (pp.6,10–14).

**Training objectives:** Eq.5 weighted clean-signal denoising squared error sum_k gamma_k² E||D(x+sigma_k epsilon,sigma_k)−x||². Preconditioning c_skip/c_out/c_in and sigma_data described §2.5. Exact chosen gamma schedule should be checked against implementation; not inferred from generic diffusion practice. Gaussian observation likelihood and SMC weights are inference operations, not extra neural training losses (§3).

**Reported evidence:** Generation EMD evaluated2–150steps, conditioned versus unconditioned and real-real references (Fig.2). R² missing-precordial-lead .98–.99 versus Dower .71–.87,95%CLT intervals (Table1). MI AUC .75 male/.70 female Fig.10, separate diagnostic task.

**Clinical utility, experts and privacy:** No augmentation/TSTR, blinded experts or privacy attack. Posterior uncertainty and random-network uncertainty have different meanings; neither establishes privacy. Healthy prior deliberately does not preserve pathology in anomaly-detection reconstruction (§3.3.4).

**Reproducibility:** Readable arXiv manuscript; equations and sampling algorithms explicit. Exact trained checkpoint and code not executed; generation metric cost mixes normalized amplitudes and condition scales.

**Critical assessment:** Healthy beats and QRS amplitude normalization restrict claims about arrhythmia, absolute voltages and long-duration HRV. Normalized R² for lead reconstruction cannot be compared to whole-record unconditional generation fidelity. EMD real-real reference is a useful design, but sample count and feature scaling must stay fixed.
