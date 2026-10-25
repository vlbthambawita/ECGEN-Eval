# rECG: A Guided Diffusion Framework for Remote Electrocardiography Reconstruction from Facial Video
- **ID / Year / Venue:** P122 / 2025 / IEEE International Joint Conference on Biometrics (IJCB)
- **Model & task:** Diffusion (Guided ECG Diffusion Model, GEDM; multi-stage, landmark-guided; PhysNet rPPG extractor); other-modality2ECG (facial video -> ECG)
- **Losses:** unknown (abstract only)
- **Evaluation:** MAE; RMSE; correlation; SNR (tags: fidelity)
- **Data:** PhysioFace Diverse Dataset (PFDD, 100 subjects); MAHNOB-HCI; leads: 1; fs: unknown (abstract only); length: unknown (abstract only)
- **Notes:** Guidance by P wave, QRS, T wave landmarks; new dataset with diverse skin tones.
- **Takeaway for ECGEN-Eval:** Paired metrics (MAE/RMSE/r/SNR) are the norm for translation tasks; ECGEN-Eval could offer a paired mode.
- *Extraction source: abstract-only*
