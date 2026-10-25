# A U-Net Based LSGAN Framework for 12-Lead ECG Synthesis in Wearable IoMT Systems
- **ID / Year / Venue:** P008 / 2026 / IEEE Internet of Things Journal
- **Model & task:** U-Net LSGAN reconstructing 12-lead ECG from leads I and II
- **Losses:** LSGAN + L1
- **Evaluation:** Mean PCC over generated leads (0.905)
- **Data:** PTB-XL, patient-wise split
- **Takeaway for ECGEN-Eval:** Per-lead PCC is the standard for lead reconstruction; report per-lead and patient-wise splits.
- *Extraction source: abstract-only*
