# UniECG: Understanding and Generating ECG in One Unified Model

**Citation:** Jiarui Jin and Haoyu Wang and Xiang Lan and Jun Li and Hongyan Li and Shenda Hong. *UniECG: Understanding and Generating ECG in One Unified Model*. arXiv, 2025. DOI: not identified. arXiv: 2509.18588v2; first public: 2025-09-23; peer-reviewed date: not verified.

**Source/version:** [paper.pdf](../papers/2025/Jin_2025_UniECG/paper.pdf); [landing.html](../papers/2025/Jin_2025_UniECG/landing.html). [Landing page](https://arxiv.org/abs/2509.18588v2).


**Task and model:** Text-conditioned 12-lead generation through eight special language-model tokens, a learned mapper, and a pretrained DiffuSETS generator; also ECG interpretation, which is a separate endpoint (pp.3–5).

**Data and split:** MIMIC-IV-ECG: 737,875 training records after excluding first 50,000 and 2,381 GEM test records; 10,000 generation test records sampled from the first 50,000. Record separation is explicit; patient separation and generator pretraining overlap are not established here. Original DiffuSETS signal preprocessing is inherited (p.5 §4.1).

**Evaluation metrics:** Generation Table 2: FID ↓, manifold precision/recall/F1 ↑, HR mean absolute error ↓ (bpm under the inherited protocol), ECG–text CLIP similarity ↑, and decoding success rate ↑. Feature extractor and implementation inherit DiffuSETS rather than being redefined. No paired raw waveform metric. GLM-5 interpretation scores in Table 1 evaluate explanations, not generated ECG clinical validity (pp.4–6).

**Training objectives:** Interpretation token negative log likelihood Eq.3. Generation token NLL Eq.4 with separate start/first/remainder lambda weights (numerical values not reported); mapper squared L2 to frozen DiffuSETS text embeddings Eq.5; total generation L_e+L_d Eq.6, unit top-level weights. Only specified embeddings, head, last eight transformer blocks, normalization, and mapper are updated; underlying waveform generator is pretrained (pp.3–5).

**Reported evidence:** Table 2: FID 79.43 versus direct DiffuSETS 25.26; recall .615 versus .709; HR error 11.72 versus 8.70; success 95.61% versus 100%. No uncertainty or isolated loss ablation reported (pp.5–6).

**Clinical utility, experts and privacy:** No completed medical-student study; human educational evaluation is future work. No membership attack, external generation validation, or TSTR experiment (pp.5–6).

**Reproducibility:** Analyzed arXiv v2 manuscript carries RespMultimodal@KDD 2026 header. Training settings given; generator inherited. Code execution and metric reproduction not performed.

**Critical assessment:** A useful counterexample to treating interface capability as improved waveform quality. Interpretation accuracy cannot substitute for validation of the separately generated teaching cases. Decoding failures should remain in the denominator.
