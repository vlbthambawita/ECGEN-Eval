# DiffuSETS: 12-Lead ECG generation conditioned on clinical text reports and patient-specific information

**Citation:** Lai Y and Chen J and Zhao Q and Zhang D and Wang Y and Geng S and Li H and Hong S. *DiffuSETS: 12-Lead ECG generation conditioned on clinical text reports and patient-specific information*. Patterns (New York, N.Y.), 2025. DOI: 10.1016/j.patter.2025.101291. arXiv: 2501.05932v1; first public: 2025-01-10; peer-reviewed date: 2025-06-11.

**Source/version:** [fulltext.xml](../papers/2025/Lai_2025_DiffuSETS/fulltext.xml); [paper.pdf](../papers/2025/Lai_2025_DiffuSETS/paper.pdf); [landing.html](../papers/2025/Lai_2025_DiffuSETS/landing.html). [Landing page](https://doi.org/10.1016/j.patter.2025.101291).


**Task and model:** Text- and patient-conditioned latent diffusion: separately trained VAE plus cross-attention U-Net; age, sex, heart rate and LLM clinical-report embeddings (Methods, Model architecture).

**Data and split:** MIMIC-IV-ECG 800,035→794,372 retained recordings; 12 leads, 10 s,500 Hz downsampled to1,024 points (effective102.4 Hz). Excludes missing demographics/undetectable HR; XQRS replaces abnormal RR values. PTB-XL21,799 external records processed identically (Methods, Datasets). Explicit generator patient-level separation unclear in these methods; downstream50,000/task split80/10/10.

**Evaluation metrics:** Net1D feature FID (Gaussian feature moment distance; Eq.12), k=3 manifold precision/recall/F1 (Eqs.13–16), conditional HR MAE bpm (Eq.17), paired text–ECG embedding cosine/CLIP score (Eq.18). No raw pointwise MAE for unpaired waveforms. FeatureDB average-wave evaluation in TableS1; detailed supplementary implementation pending. Net1D/contrastive encoder training corpus and independence insufficiently specified in main paper. Diagnosis classifier outcomes and cardiologist real/fake judgments plus text-condition correctness (Results).

**Training objectives:** VAE MSE reconstruction+lambda KL(q(z|x)||N(0,I)); lambda linearly annealed from0, terminal value not specified (Eqs.7–8). Latent diffusion noise prediction MSE (Methods, Eq.5). VAE pretrained separately; T=1000, beta schedule0.00085–0.012, latent4×128; optimizer LR5e−4,batch512 (Implementation details). KL expression printed with log sigma rather than an unambiguously conventional variance notation; use faithful distributional Eq.7.

**Reported evidence:** Table1 internal FID23.6, manifoldF1 .894, HRMAE4.15, CLIP .812. Without patient information HRMAE12.25; without VAE FID48.9. These are component/conditioning ablations, not isolated KL-weight ablations. External PTB-XL FID27.6/HRMAE6.73. No claim of cross-paper ranking.

**Clinical utility, experts and privacy:** Minority augmentation versus real-only and weighted-CE baselines for normality,AF,PVC; 50,000 selected records/task,80/10/10. Two cardiologists evaluate50 generated+50 real ECGs;100 generated reports assessed for semantic correctness (76%). Expertise years, agreement and uncertainty not fully specified (Results, Turing test; Fig.3). No membership attack or formal privacy guarantee.

**Reproducibility:** Published full text analyzed, linked arXiv v1 retained as earlier version. https://github.com/PKUDigitalHealth/DiffuSETS and https://doi.org/10.5281/zenodo.15331141; no code inspection. Supplement-specific metrics remain explicitly incomplete until supplement retrieval.

**Critical assessment:** Reviewer assessment: broad evaluation spanning distribution, coverage, conditions and experts; encoder dependence, split independence and privacy claims require stronger checks.
