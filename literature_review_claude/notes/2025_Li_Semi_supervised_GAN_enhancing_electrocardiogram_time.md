# Semi-supervised GAN for enhancing electrocardiogram time series diagnostics
- **ID / Year / Venue:** P128 / 2025 / Biomedical Signal Processing and Control
- **Model & task:** TimeGAN-style recurrent GAN (embedding/recovery autoencoder, latent RNN generator and bidirectional RNN discriminator; GRU/LSTM/LSTM-LN cells); class-wise synthesis of RBBB/RVOT/LVOT/Brugada/normal ECG for class balancing
- **Losses:** Reconstruction + latent adversarial BCE + supervised next-step latent loss
- **Evaluation:** t-SNE/PCA; discriminative score (post-hoc real-vs-synthetic RNN); predictive score (train-on-synthetic next-step MAE); ResNet-18 accuracy/sensitivity/specificity with real, real+synthetic and synthetic-only training; comparisons with oversampling, RCGAN, GES, Nef-Net [fidelity, diversity, utility-TSTR]
- **Data:** Private Guangdong hospital, 653 patients; leads: not reported (12-lead source); fs: 360 Hz; length: 10 s classifier input (13.89 s stated)
- **Notes:** Discriminative score 0.179 (GRU); augmentation 91.25→94.04%; synthetic-only 97.2% beats real-only 92.1%. Title says semi-supervised GAN but it is a TimeGAN variant. 100-record test set, inconsistent patient counts, no waveform/clinical metrics.
- **Takeaway for ECGEN-Eval:** ECGEN-Eval could add TimeGAN's discriminative score (post-hoc classifier two-sample test) and predictive score as optional metrics, and should report confidence intervals since tiny test sets like this make small accuracy gains uninterpretable.
- *Extraction source: full-text*
