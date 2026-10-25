# ECG Synthesis and Utility Analysis - A Diffusion Model Based Approach
- **ID / Year / Venue:** P060 / 2025 / Studies in health technology and informatics
- **Model & task:** Diffusion (SSSD-ECG adaptation); class-cond (Normal sinus rhythm vs AF)
- **Losses:** unknown (abstract only)
- **Evaluation:** TSTR F1 (train synthetic features, test real: 0.80); TRTS F1 (0.91); blinded physician Turing-style tests at two university hospitals
- **Data:** MIMIC-IV-ECG; leads: 12; fs: unknown (abstract only); length: 10
- **Takeaway for ECGEN-Eval:** Report TSTR and TRTS together; multi-site blinded clinician test as gold-standard realism check.
- *Extraction source: abstract-only*
