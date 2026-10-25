# Complementarity-Preserving Generative Theory for Multimodal ECG Synthesis: A Quantum-Inspired Approach

**Citation:** Timothy Oladunni and Farouk Ganiyu-Adewumi and Clyde Baidoo and Kyndal Maclin. *Complementarity-Preserving Generative Theory for Multimodal ECG Synthesis: A Quantum-Inspired Approach*. arXiv, 2026. DOI: not identified. arXiv: 2603.26695v1; first public: 2026-03-16; peer-reviewed date: not verified.

**Source/version:** [paper.pdf](../papers/2026/Oladunni_2026_Complementarity/paper.pdf); [landing.html](../papers/2026/Oladunni_2026_Complementarity/landing.html). [Landing page](https://arxiv.org/abs/2603.26695v1).


**Task and model:** Q-CFD-GAN with complex latent coupling and time/frequency/scalogram decoders; includes waveform output (§IV).

**Data and split:** Mendeley multimodal ECG source;70/15/15 patient-level split asserted. 0.5–40Hz bandpass,baseline correction,amplitude normalization,1,000sample segments; STFT256 Hann/50%overlap and Morlet scalogram. Sample counts,lead configuration,Hz and cohort details insufficiently specified (§IV.B,§V.A).

**Evaluation metrics:** Embedding variance/excess-variance ratio; classifier-output KL plausibility gap Delta; relative reduction rho; mutual-information complementarity retention and gamma; RMS-energy deviation and kappa; P2P amplitude,spectral entropy and joint RMS/P2P plots (Eqs.1–4,15,TableIII,Figs3–6). Encoder/classifier provenance and MI estimator details unclear; dimensionless normalized scores are specific to this paper.

**Training objectives:** Eq.11/Algorithm1: adversarial+lambda1 CFD+lambda2 interference+lambda3 physiology; CFD aligns complementarity plus orthogonality penalty (Eq.9), interference matches energy (Eq.13), physiology penalizes QRS/ST discrepancy (Eq.10). Critic WGAN-GP. Eq.14 instead omits adversarial term and weights: unresolved inconsistency. Lambda values grid-searched but not reported (§V.B).

**Reported evidence:** TableIII variance .033 vs real .031; classifierKL .157 vs MI-GAN .214; complementarity retention .91 vs .56; RMS3.8% vs11.2%. No uncertainty. Loss-removal ablations listed in design but component-specific numerical results not clearly separated in TableIII.

**Clinical utility, experts and privacy:** Classifier plausibility proxy, no reported TSTR or independent cardiologist panel; no empirical privacy validation.

**Reproducibility:** Unspecified dataset size, trained feature models, MI estimation and selected coefficients impede reproduction; preprint analyzed.

**Critical assessment:** Reviewer assessment: proposed signal constraints warrant testing, but stationary loss conditions and classifier agreement do not by themselves establish clinical validity or the claimed mathematical necessity of complex latents.
