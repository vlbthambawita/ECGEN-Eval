# L2L-ESN: A Lead-to-Lead Electrocardiogram Synthesis Network for Assisting Myocardial Infarction Diagnosis
- **ID / Year / Venue:** P097 / 2026 / Intelligent Computing
- **Model & task:** GAN (conditional Wasserstein, multi-head generator); lead-reconstruction (reduced leads -> 12-lead) + MI localization
- **Losses:** conditional WGAN adversarial (other terms unknown, abstract only)
- **Evaluation:** waveform similarity metrics (unspecified); downstream MI diagnostic accuracy; qualitative visualization; deployment profiling [fidelity; utility-TSTR; efficiency]
- **Data:** 2 real-world ECG datasets (unnamed in abstract); leads: 12 (output); fs: unknown (abstract only) Hz; length: unknown (abstract only) s
- **Notes:** Includes deployment profiling (IoMT efficiency) as part of evaluation.
- **Takeaway for ECGEN-Eval:** Downstream diagnostic accuracy on reconstructed leads and compute profiling complement waveform similarity.
- *Extraction source: abstract-only*
