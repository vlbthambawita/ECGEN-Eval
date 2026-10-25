# MM-DADM: Multimodal Drug-Aware Diffusion Model for Virtual Clinical Trials
- **ID / Year / Venue:** P104 / 2025 / arXiv
- **Model & task:** Diffusion (DDPM backbone with pharmacokinetic ODE fusion via dynamic cross-attention + counterfactual drug-aware ControlNet-style CDC-Net; contrastive causal feature encoder); other-modality2ECG / class-cond (drug- and demographics-conditioned post-dose ECG from pre-dose ECG; virtual clinical trials)
- **Losses:** DDPM epsilon-prediction MSE (L_bb, L_real) + lambda*causal guidance loss L_cau (1 - cosine sim to drug prototypes, lambda=0.1) for counterfactual samples; supervised contrastive loss L_con for the causal feature encoder
- **Evaluation:** accuracy/recall of normal-vs-abnormal status agreement on QTc (Bazett), PR, Tpeak-Tend intervals (single and multi-indicator); Fréchet ResNet Distance (FRD); RMSE; cardiologist real-vs-generated discrimination accuracy (10 cardiologists, 100 ECGs per lead per method); downstream ResNet-1D drug-administration classification with 100/200/500 synthetic augmentations [clinical; distribution; fidelity; expert; utility-TSTR]
- **Data:** ECGRDVQ and ECGDMMLD (FDA drug trials; 9,443 12-lead ECGs, 44 subjects, 8 regimens); leads: 12 (8 generated: I, aVF, V1-V6; 4 limb leads derived); fs: 1000 (recording rate) Hz; length: 10 s
- **Notes:** FRD 0.2431, RMSE 0.0127 vs SSSD-ECG 0.4719/0.0312 and FlowECG 0.5164. Expert Turing test: ideal is ~50% accuracy; MM-DADM near chance. Clinical-interval threshold agreement (normal/abnormal) is a novel clinically-grounded metric. Compares 10 baselines.
- **Takeaway for ECGEN-Eval:** Adopt FRD with a pretrained 1D ResNet, interval-category agreement (QTc/PR/Tpeak-Tend normal ranges), and a Turing-test protocol.
- *Extraction source: full-text*
