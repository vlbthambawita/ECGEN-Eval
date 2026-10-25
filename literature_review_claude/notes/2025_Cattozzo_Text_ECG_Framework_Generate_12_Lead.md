# Text-to-ECG: a Framework to Generate 12-Lead ECG from Text Reports
- **ID / Year / Venue:** P144 / 2025 / Annual International Conference of the IEEE Engineering in Medicine and Biology Society. IEEE Engineering in Medicine and Biology Society. Annual International Conference
- **Model & task:** Text-to-ECG: Bio_ClinicalBERT embedding -> WGAN-GP generating 12-lead beats
- **Losses:** WGAN-GP
- **Evaluation:** Visual inspection + quantitative realism assessments; ASMI class failed
- **Data:** PTB-XL, 5 diagnostic classes
- **Takeaway for ECGEN-Eval:** Per-class evaluation reveals class-specific failures hidden by pooled metrics.
- *Extraction source: abstract-only*
