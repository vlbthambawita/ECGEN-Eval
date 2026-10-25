# PPGFlowECG: Latent Rectified Flow with Cross-Modal Encoding for PPG-Guided ECG Generation and Cardiovascular Disease Detection
- **ID / Year / Venue:** P118 / 2025 / arXiv
- **Model & task:** FlowMatching (latent rectified flow, Transformer velocity field with cross-attention; CardioAlign VAE-style cross-modal encoder); PPG2ECG
- **Losses:** Stage 1 CardioAlign: Global Distribution Alignment (L2 mean + symmetric KL), Local Instance Discrimination (InfoNCE contrastive), Semantic Decodability Constraint (cross-modal L2 reconstruction), plus waveform reconstruction; Stage 2: rectified-flow MSE velocity loss
- **Evaluation:** MAE; RMSE; MAE of heart rate (MAEHR, Hamilton detector); downstream per-class AUROC and Macro-AUROC (MCMED multi-label CVD); AF accuracy and F1 (MIMIC-AFib, internal/external); saliency/attribution map comparison; clinical Turing test (5 cardiologists, 100 signals); cardiologist AF diagnosis with PPG only vs PPG+real vs PPG+synthetic ECG; sampling-step ablation
- **Data:** MCMED; MIMIC-AFib; VitalDB; BIDMC; leads: 1 (Lead II); fs: 128; length: 10
- **Takeaway for ECGEN-Eval:** Expert 'diagnostic-utility' reader study (real vs synthetic as diagnostic aid) is a strong protocol beyond Turing tests.
- *Extraction source: full-text*
