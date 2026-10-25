# Wearable health monitoring with seismocardiography and generative modeling
- **ID / Year / Venue:** P153 / 2025 / eScholarship@McGill (McGill)
- **Model & task:** Other (thesis; generative models for SCG and SCG->multimodal reconstruction); other-modality2ECG (SCG -> ECG/ICG/PPG/NIBP); augmentation (synthetic SCG)
- **Losses:** unknown (abstract only)
- **Evaluation:** median correlation of reconstructed signals (ECG 0.808, NIBP 0.907, ICG 0.833, PPG 0.929); AUROC of OOD pulmonary hypertension detection with synthetic data (0.51 -> 0.86) (tags: fidelity;utility-TSTR)
- **Data:** unknown (abstract only); leads: unknown (abstract only); fs: unknown (abstract only); length: unknown (abstract only)
- **Notes:** Thesis primarily on seismocardiography; synthetic data mainly SCG not ECG. Introduces a dataset selection method for mixing synthetic and real training data.
- **Takeaway for ECGEN-Eval:** Marginal relevance; synthetic-data selection for OOD utility is an interesting utility-evaluation angle.
- *Extraction source: abstract-only*
