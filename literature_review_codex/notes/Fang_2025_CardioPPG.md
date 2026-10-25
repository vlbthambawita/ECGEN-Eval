# AI modeling photoplethysmography to electrocardiography useful for predicting cardiovascular disease

**Citation:** Ding Z and Hu Y and Li Z and Mao Y and Li H and Zhou D and Chu X and Yu L and Liu Z and Wu F and Zhang H and Xu Q and Chen T and Huang Z. *AI modeling photoplethysmography to electrocardiography useful for predicting cardiovascular disease*. NPJ digital medicine, 2025. DOI: 10.1038/s41746-025-02228-3. arXiv: not applicable; first public: 2025-12-14; peer-reviewed date: 2025-12-14.

**Source/version:** [fulltext.xml](../papers/2025/Fang_2025_CardioPPG/fulltext.xml). [Landing page](https://doi.org/10.1038/s41746-025-02228-3).


**Task and model:** CardioPPG translates PPG to ECG with STFT low/high bands, quantized VQ-VAE tokens and PPG-conditioned bidirectional transformers that iteratively reveal masked tokens (npj Digital Medicine 2025; Methods “Conditional generative model with TimeVQVAE”).

**Data and split:** Paired 10-s ECG/PPG windows standardized to 256Hz, amplitudes [-1,1], no explicit lag correction. Source 8,942,348 paired segments over 3 sources; PulseDB-MIMIC subset split 70/10/20 by subject for downstream tasks; external ring AF train44/test40 subjects. Generation metric cohort/count details appear supplemental and were unavailable.

**Evaluation metrics:** MAE/MSE ↓ paired waveforms, PSNR/SSIM ↑, FID ↓ with ROCKET features, FD ↓ raw first/second moments, MDD marginal density, ACD autocorrelation difference, SD/KD skew/kurtosis differences. 95% bootstrap CIs, 1000 resamples; STFT window n32 vs16/64/128. No expert or privacy attack in main article (“Quality assessment…”).

**Training objectives:** VQ stage STFT32, separate LF/HF encoders/codebooks; summed squared dictionary and beta commitment terms plus LF/HF reconstruction L2; beta unspecified. Frozen quantizer/decoder in stage2. Two masked-token cross entropies: LF tokens conditional on masked LF and PPG; HF conditional on LF, masked HF and PPG; iterative masked inference with cosine schedule. Contrastive pretraining bidirectional CE tau=.05 (Methods).

**Reported evidence:** Text states CardioPPG beats RDDM/WGAN/RecQRS on most metrics; examples FID .001 vs .008 and ACD .367 vs31.046. 1000-bootstrap CIs in supplement. No explicit isolated loss ablation in extracted methods.

**Clinical utility, experts and privacy:** Primary emphasis is CVD screening with subject-level cohorts and external smart-ring PPG AF test. This supports utility for that task, not independently diagnostic waveform validity. No generated ECG clinician blinding/privacy reported. Code URL github.com/Yukui-1999/CardioPPG.

**Reproducibility:** Published full text and code URL available. Detailed CIs and generation cohort are supplemental; supplement not locally available and was not used.

**Critical assessment:** PPG-to-ECG lag is not corrected; paired MAE can penalize phase offsets and cannot be compared with unconditional generation. Feature/distribution scores depend on ROCKET and preprocessing.
