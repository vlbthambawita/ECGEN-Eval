# Disentangled conditional generation of ECG signals with interpretable latent factors
- **ID / Year / Venue:** P051 / 2026 / Computer Methods and Programs in Biomedicine
- **Model & task:** Hybrid (beta-TC-VAE with self-attention + conditional normalizing flow prior in latent space); class-cond (controllable, disentangled generation)
- **Losses:** beta-Total-Correlation VAE objective (reconstruction + KL with TC penalty); conditional flow (likelihood) in latent space
- **Evaluation:** mutual information gap (MIG, proxy-based) for disentanglement; fidelity; diversity
- **Data:** unknown (abstract only); includes an out-of-domain target dataset; leads: unknown (abstract only); fs: unknown (abstract only); length: unknown (abstract only)
- **Takeaway for ECGEN-Eval:** Separate fidelity vs diversity scores (precision/recall-style) and disentanglement metrics (MIG) are useful for conditional/controllable models.
- *Extraction source: abstract-only*
