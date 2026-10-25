# Continuous multi-step ECG and PPG generation through latent disentanglement
- **ID / Year / Venue:** P161 / 2026 / Computers in Biology and Medicine
- **Model & task:** Hybrid (autoencoder + adversarial latent disentanglement, recurrent); other (subject-conditional multi-step continuation; style transfer)
- **Losses:** reconstruction + adversarial disentanglement (details unknown, abstract only)
- **Evaluation:** unknown (abstract only); within-recording segment-level protocol [unknown (abstract only)]
- **Data:** ECG 17 subjects; PPG 7 subjects (datasets unnamed in abstract); leads: unknown (abstract only); fs: unknown (abstract only) Hz; length: ~6 s generated (up to ~8 s for some subjects) s
- **Notes:** Long-horizon multi-step generation; quality degrades beyond ~6 s. Within-recording evaluation protocol limits generalization claims.
- **Takeaway for ECGEN-Eval:** Metrics as a function of generation horizon (degradation over time) would suit autoregressive/continuation models.
- *Extraction source: abstract-only*
