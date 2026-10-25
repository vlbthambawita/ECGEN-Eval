# f-GAN: A frequency-domain-constrained generative adversarial network for PPG to ECG synthesis

**Citation:** Nathan C. L. Kong and Dae Lee and Huyen Do and Dae Hoon Park and Cong Xu and Hongda Mao and Jonathan Chung. *f-GAN: A frequency-domain-constrained generative adversarial network for PPG to ECG synthesis*. arXiv, 2024. DOI: not identified. arXiv: 2406.16896v1; first public: 2024-05-15; peer-reviewed date: not verified.

**Source/version:** [paper.pdf](../papers/2024/Kong_2024_fGAN/paper.pdf); [landing.html](../papers/2024/Kong_2024_fGAN/landing.html). [Landing page](https://arxiv.org/abs/2406.16896v1).


**Task and model:** PPG-conditioned attention-gated U-Net GAN for paired ECG waveform synthesis (§2.2–2.3).

**Data and split:** 15 participants,9/3/3 disjoint train/validation/test subjects;40,675/11,276/12,796 training-length segments. Resample128Hz,4s windows with2s overlap; PPG0.4–8Hz,ECG3–45Hz filters,minmax[−1,1]. Evaluate10s windows with8s overlap (§2.1,2.5); external cohort not reported.

**Evaluation metrics:** HR MAPE%=100/N sum|HRreal−HRgen|/HRreal; standard peak detector and count of HR extraction failures. Validation mean/SD across31 seeds; best-validation-seed testMAPE; active/inactive strata; visual ECG morphology (§2.5,§3,Eq.4).

**Training objectives:** Original logistic adversarial minimax+0.1×paired L1 FFT-amplitude difference excluding DC. Generator minimizes both, discriminator maximizes adversarial term (Eqs.1–3). Time-domain paired loss deliberately avoided for PPG–ECG latency. Generator/discriminator LR1e−4/1e−5; updates5:1; baseline15epochs vs spectral11epochs (§2.4).

**Reported evidence:** 31 seeds each arm: validation MAPE SD12%→3%; t(60)=3.04,p=.005; failure counts t(60)=2.97,p=.006. Best-seed testMAPE14%→12%, PPG detector15% (Figs3–5,Table1). Different epoch schedules are a residual confound.

**Clinical utility, experts and privacy:** HR extraction is utility, not disease diagnosis. No expert, privacy attack or independent external validation reported.

**Reproducibility:** FFT coefficient and exclusions explicit, more seeds than most reviewed studies. Peak-detection failures reported rather than silently omitted. Dataset name verified from p.1 during final check; no source code inspected.

**Critical assessment:** Reviewer assessment: relatively direct evidence for one spectral term, limited to HR and a small healthy/wearable cohort; correct HR does not validate ST/QT morphology.
