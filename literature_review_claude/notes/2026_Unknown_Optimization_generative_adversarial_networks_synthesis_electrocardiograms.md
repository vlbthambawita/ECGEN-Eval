# Optimization of generative-adversarial networks for the synthesis of electrocardiograms by adaptive quantization
- **ID / Year / Venue:** P110 / 2026 / Herald of Dagestan State Technical University Technical Sciences
- **Model & task:** GAN (MeGAN: BiLSTM generator, CNN discriminator) + post-training weight quantization (AGWR vs Min-Max); unconditional; model compression
- **Losses:** standard GAN adversarial (BCE, sigmoid discriminator)
- **Evaluation:** Frechet Distance (Gaussian on feature space); PSNR; SSIM; Pearson correlation (quantized vs original model outputs); memory consumption
- **Data:** stated as MIT-BIH Arrhythmia (described as 10 s, 500 Hz, 12-lead, which is inconsistent with MIT-BIH); leads: 12 (as stated); fs: 500 (as stated); length: 10 (as stated)
- **Takeaway for ECGEN-Eval:** Example of FD values without stated embedding model; ECGEN-Eval should report extractor and scale for every Frechet metric.
- *Extraction source: full-text*
