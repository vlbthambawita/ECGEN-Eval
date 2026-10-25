# Boosting EEG and ECG Classification with Synthetic Biophysical Data Generated via Generative Adversarial Networks
- **ID / Year / Venue:** P026 / 2024 / Applied Sciences
- **Model & task:** GAN (WGAN-GP; also vanilla GAN baseline); augmentation (EEG mental states; ECG normal/abnormal)
- **Losses:** WGAN-GP: critic loss D(fake)-D(real)+lambda*GP (lambda=10); generator -D(fake); post-hoc smoothing (window 10) of synthetic ECG
- **Evaluation:** classification accuracy (SVM, RF) trained on real tested on real/synthetic/combined, and with real+synthetic training at varying synthetic proportions; PSD plots (EEG); visual inspection [utility-TSTR]
- **Data:** ECG: Kaggle ECG dataset (140-point beats, normal/abnormal labels); EEG: Bird et al. Muse dataset (TP9, AF7, AF8, TP10); leads: 1 (ECG); fs: not reported Hz; length: not reported (140 samples per ECG) s
- **Notes:** ECG RF accuracy 97% real -> 98.40% with synthetic. Train-on-real/test-on-synthetic (TRTS) used as quality check. Post-hoc smoothing applied to remove GAN spikes, which may mask generator artefacts. No distributional metrics.
- **Takeaway for ECGEN-Eval:** TRTS (classifier trained on real, tested on synthetic) is a cheap complementary utility metric; flag post-processing that hides artefacts.
- *Extraction source: full-text*
