# FlowECG: Using Flow Matching to Create a More Efficient ECG Signal Generator

**Citation:** Vitalii Bondar and Serhii Semenov and Vira Babenko and Dmytro Holovniak. *FlowECG: Using Flow Matching to Create a More Efficient ECG Signal Generator*. arXiv, 2025. DOI: 10.1007/978-3-032-18415-3_32. arXiv: 2509.10491v1; first public: 2025-08-31; peer-reviewed date: not verified.

**Source/version:** [paper.pdf](../papers/2025/Bondar_2025_FlowECG/paper.pdf); [landing.html](../papers/2025/Bondar_2025_FlowECG/landing.html). [Landing page](https://arxiv.org/abs/2509.10491v1).


**Task and model:** Diagnosis-conditioned S4 flow matching, retaining SSSD-ECG architecture; 71 binary diagnostic conditions (pp. 2–5, §§2.1,3.1–3.2).

**Data and split:** PTB-XL: 21,799 recordings/18,869 patients; 10 s, 1,000 samples, 8 independently generated leads expanded to 12. Hold-out test stated, but fold numbers, split sizes and explicit patient separation unclear; normalization not reported (pp. 2,4).

**Evaluation metrics:** DTW (Eq.3), feature-based 1-Wasserstein (Eq.4), spectral similarity 1/(1+mean PSD Wasserstein) (Eq.5), biased empirical squared MMD (Eqs.6–7), and neural function evaluations/NFE. Lead-average aggregation is stated, but Wasserstein also concatenates channel features; exact feature list, kernel/bandwidth, and DTW pairing are unclear (§2.3). Errors lower, spectral similarity higher; units depend on preprocessing. NFE is a computation proxy, not wall-clock latency.

**Training objectives:** Velocity regression E||f_theta(x_t,c,t)−(x_1−x_0)||², x_t a linear interpolation of independent Gaussian noise and ECG; unit coefficient; uniform time sampling; generator network only. Adam 2e−4, batch 6; Euler inference (Eq.8, pp.4–5).

**Reported evidence:** Matched-backbone comparison and NFE sweep, not an isolated regularizer ablation. Table 1 reports MMD 80.70→21.09 and DTW 73.49→83.96 at 200 NFE; lower DTW is better, so it worsens. Claims of improvement on three metrics conflict with prose acknowledging spectral worsening; retain table-specific comparisons, not the headline. 10–25 NFE performance is claimed from Fig.2 (§3.3).

**Clinical utility, experts and privacy:** No downstream classification experiment, blinded clinical panel, or empirical privacy attack reported. Privacy is motivation, not a demonstrated guarantee (whole main text).

**Reproducibility:** Architecture and optimizer specified; uncertainty, repeated seeds and full metric implementation details not reported. Publication footnote says preprint not peer reviewed and proceedings version forthcoming (p.1); do not treat this as confirmed publication.

**Critical assessment:** Reviewer assessment: useful efficiency evidence, but NFE must be paired with time/hardware measurements; feature distributions and unpaired DTW cannot independently establish physiological validity.
