# ECG Monitor Design: From One to Three - Advancing ECG Monitoring with AI-Generated Lead Synthesis (GANs)
- **ID / Year / Venue:** P057 / 2024 / IEEE International Conference on Artificial Intelligence & Green Energy (ICAIGE)
- **Model & task:** GAN (conv encoder-decoder generator, conv discriminator pre-trained after Fawaz et al.); lead reconstruction I→II, III for a reduced-electrode 3-lead monitor (paper also describes AD620/Arduino hardware)
- **Losses:** adversarial loss (unspecified); claimed 'medical constraints' are not described in the body
- **Evaluation:** paired MSE/RMSE and Pearson r for leads II and III; comparison to numbers from prior CNN/LSTM/linear-regression work; visual comparison [fidelity]
- **Data:** CPSC 2018; PTB-XL; private hospital data; leads: 3 (1 in, 2 generated); fs: not reported Hz; length: not reported s
- **Notes:** Lead II MSE 0.0123, r 0.98; lead III MSE 0.0154, r 0.97; summary RMSE 0.0119, r 0.998. Tables mix MSE and RMSE, the Pearson formula and lead equations are printed incorrectly, baselines are copied from other papers, and there is no clinical evaluation.
- **Takeaway for ECGEN-Eval:** For lead-reconstruction tasks ECGEN-Eval should offer an explicitly paired mode (per-lead RMSE, Pearson r) plus an Einthoven consistency check (III = II - I), since a single-lead input cannot determine II and III and such papers lack any physiological sanity test.
- *Extraction source: full-text*
