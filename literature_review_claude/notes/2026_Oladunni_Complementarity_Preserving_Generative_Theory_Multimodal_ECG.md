# Complementarity-Preserving Generative Theory for Multimodal ECG Synthesis: A Quantum-Inspired Approach
- **ID / Year / Venue:** P036 / 2026 / arXiv
- **Model & task:** GAN (quantum-inspired Q-CFD-GAN, complex-valued latent, Hermitian interference operator, tri-domain decoder); unconditional (multimodal: time, STFT spectrum, time-frequency scalogram of beats)
- **Losses:** adversarial with gradient penalty + lambda1*CFD complementarity loss (tri-domain complementarity alignment + orthogonality penalty) + lambda2*interference-preserving loss + lambda3*physiological morphology loss (QRS and ST L2 terms)
- **Evaluation:** embedding variance and excess-variance ratio (pretrained multimodal encoder); classifier-based plausibility gap (KL divergence of pretrained classifier outputs real vs synthetic); tri-domain complementarity retention; RMS energy deviation (%); morphology contraction coefficient; peak-to-peak amplitude, RMS energy and spectral entropy distributions; RMS-P2P joint manifold [distribution; clinical; fidelity]
- **Data:** multimodal ECG dataset from Mendeley Data (patient-level 70/15/15 split); leads: not reported; fs: not reported Hz; length: not reported (beats padded/truncated to 1000 samples) s
- **Notes:** Novel classifier-output KL 'plausibility gap' (0.157 vs 0.214 for MI-GAN) and cross-domain complementarity retention (0.91). Metrics derived from their own theory; single dataset; no TSTR or expert evaluation.
- **Takeaway for ECGEN-Eval:** Classifier-output KL plausibility gap and P2P/RMS/spectral-entropy distribution plots are easy additions.
- *Extraction source: full-text*
