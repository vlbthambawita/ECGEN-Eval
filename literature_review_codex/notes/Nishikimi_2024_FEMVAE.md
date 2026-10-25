# Variational autoencoder-based neural electrocardiogram synthesis trained by FEM-based heart simulator

**Citation:** Nishikimi R and Nakano M and Kashino K and Tsukada S. *Variational autoencoder-based neural electrocardiogram synthesis trained by FEM-based heart simulator*. Cardiovascular digital health journal, 2024. DOI: 10.1016/j.cvdhj.2023.12.002. arXiv: not applicable; first public: 2023-12-22; peer-reviewed date: 2023-12-22.

**Source/version:** [fulltext.xml](../papers/2024/Nishikimi_2024_FEMVAE/fulltext.xml). [Landing page](https://doi.org/10.1016/j.cvdhj.2023.12.002).


**Task and model:** Conditional Gaussian VAE emulator of UT-Heart finite-element simulations, parameter-conditioned12-lead synthesis; qualifies because learned generator is evaluated (Methods,Model).

**Data and split:** 2,880 simulated ECG parameter combinations,16cardiac parameters encoded24dimensions;random1728/576/576 train/val/test;500samples/1s beat at500Hz,HRfixed60;ECG/1024 normalization. No real-patient training or external validation (Dataset,Experimental condition). Online publication2023-12-22;2024 issue.

**Evaluation metrics:** Paired Q/R/S/T position MAE in samples,convert to seconds /500; manually marked simulator references versus NeuroKit2 generated landmarks. PSNR=10log10(1/MSE) dB after[0,1]normalization. Abnormal landmark detections excluded; P-wave assessment omitted because identical template (Experimental condition,Table2).

**Training objectives:** Maximize conditional ELBO: expected Gaussian decoder log-likelihood minus KL(q(z|x,Y)||N(0,I));unit KL coefficient,encoder and decoder learned jointly (Training). Inference fixes z=0 rather than sampling (Inference).

**Reported evidence:** Grid over4–10layers and latent2–128;largest latent improves PSNR,optimal depth5–7;NeuroKit2 reference Q/S errors7.58/19.15samples dominate landmark evaluation (Results,Table2,Figs3–6). Architecture ablation,not KL ablation.

**Clinical utility, experts and privacy:** Medical specialist supervises ground-truth landmarks,not blinded realism test. No downstream classifier or privacy evaluation; patient separation not applicable to simulated parameter combinations.

**Reproducibility:** Simulator source cited. Annotation exclusion rule contains inconsistent150ms/100samples conversion; preserve rather than correct. Seed/run uncertainty not reported.

**Critical assessment:** Reviewer: excellent example of defensible paired errors, but emulator accuracy against a simulator is not clinical distribution coverage; z=0 results cannot support stochastic diversity.
