# References

Papers behind the metrics, models and features implemented in ECGEN-Eval.

## Metrics

| Metric | Reference |
|---|---|
| `mmd` | Gretton, A., Borgwardt, K. M., Rasch, M. J., Schölkopf, B., & Smola, A. (2012). A kernel two-sample test. *JMLR*, 13, 723–773. [Link](https://jmlr.org/papers/v13/gretton12a.html) |
| `dtw` | Berndt, D. J., & Clifford, J. (1994). Using dynamic time warping to find patterns in time series. *KDD Workshop*, 359–370. |
| `prd`, `mae` | Zigel, Y., Cohen, A., & Katz, A. (2000). The weighted diagnostic distortion (WDD) measure for ECG signal compression. *IEEE TBME*, 47(11), 1422–1430. [doi:10.1109/10.871206](https://doi.org/10.1109/10.871206) |
| `psd` | Welch, P. D. (1967). The use of fast Fourier transform for the estimation of power spectra. *IEEE Trans. Audio Electroacoust.*, 15(2), 70–73. [doi:10.1109/TAU.1967.1161901](https://doi.org/10.1109/TAU.1967.1161901) |
| `fd`, `fed` | Heusel, M., Ramsauer, H., Unterthiner, T., Nessler, B., & Hochreiter, S. (2017). GANs trained by a two time-scale update rule converge to a local Nash equilibrium. *NeurIPS*, 30. [arXiv:1706.08500](https://arxiv.org/abs/1706.08500) |
| `fed` | Kilgour, K., Zuluaga, M., Roblek, D., & Sharifi, M. (2019). Fréchet Audio Distance: A reference-free metric for evaluating music enhancement algorithms. *Interspeech*. |
| `psnr` | Huynh-Thu, Q., & Ghanbari, M. (2008). Scope of validity of PSNR in image/video quality assessment. *Electronics Letters*, 44(13), 800–801. [doi:10.1049/el:20080522](https://doi.org/10.1049/el:20080522) |
| `ssim` | Wang, Z., Bovik, A. C., Sheikh, H. R., & Simoncelli, E. P. (2004). Image quality assessment: from error visibility to structural similarity. *IEEE TIP*, 13(4), 600–612. [doi:10.1109/TIP.2003.819861](https://doi.org/10.1109/TIP.2003.819861) |
| `swd` | Kolouri, S., Nadjahi, K., Simsekli, U., Badeau, R., & Rohde, G. (2019). Generalized sliced Wasserstein distances. *NeurIPS*, 32. |
| `pr_dist` | Kynkäänniemi, T., Karras, T., Laine, S., Lehtinen, J., & Aila, T. (2019). Improved precision and recall metric for assessing generative models. *NeurIPS*, 32. |
| `hrv` | Task Force of the ESC and NASPE (1996). Heart rate variability: standards of measurement, physiological interpretation, and clinical use. *Circulation*, 93(5), 1043–1065. [doi:10.1161/01.CIR.93.5.1043](https://doi.org/10.1161/01.CIR.93.5.1043) |
| `heart_rate` | Pan, J., & Tompkins, W. J. (1985). A real-time QRS detection algorithm. *IEEE TBME*, 32(3), 230–236. [doi:10.1109/TBME.1985.325532](https://doi.org/10.1109/TBME.1985.325532) |
| `sqi` | Clifford, G. D., et al. (2017). AF classification from a short single lead ECG recording: the PhysioNet/Computing in Cardiology Challenge 2017. *CinC*, 44. [doi:10.22489/CinC.2017.065-469](https://doi.org/10.22489/CinC.2017.065-469) |
| `nn_dist` | Meehan, C., Chaudhuri, K., & Dasgupta, S. (2020). A non-parametric test to detect data-copying in generative models. *AISTATS*. |
| `spectral_entropy` | Inouye, T., et al. (1991). Quantification of EEG irregularity by use of the entropy of the power spectrum. *EEG Clin. Neurophysiol.*, 79(3), 204–210. [doi:10.1016/0013-4694(91)90138-T](https://doi.org/10.1016/0013-4694(91)90138-T) |

## ECG generation and evaluation

- Thambawita, V., et al. (2021). DeepFake electrocardiograms using generative adversarial
  networks are the beginning of the end for privacy issues in medicine. *Scientific Reports*,
  11, 21896. [doi:10.1038/s41598-021-01295-2](https://doi.org/10.1038/s41598-021-01295-2)
- Golany, T., & Radinsky, K. (2019). PGANs: Personalized generative adversarial networks for
  ECG synthesis to improve patient-specific deep ECG classification. *AAAI*, 33, 557–564.
  [doi:10.1609/aaai.v33i01.3301557](https://doi.org/10.1609/aaai.v33i01.3301557)

## Foundation models (FED backbones)

- **ECGFounder** — Li, J., et al. ECGFounder: An ECG foundation model built on over 10 million
  recordings with expert annotations. *NEJM AI* (2025). [arXiv:2410.04133](https://arxiv.org/abs/2410.04133)
- **HuBERT-ECG** — Coppola, E., et al. HuBERT-ECG: a foundation model for broad-scope ECG
  tasks. *medRxiv* 2024.11.14.24317328.
- **ECG-FM** — McKeen, K., et al. ECG-FM: An open electrocardiogram foundation model.
  *JAMIA Open* (2025). [arXiv:2408.05178](https://arxiv.org/abs/2408.05178)

## Clinical features

- Makowski, D., et al. (2021). NeuroKit2: A Python toolbox for neurophysiological signal
  processing. *Behavior Research Methods*, 53, 1689–1696.
- Bazett, H. C. (1920). An analysis of the time-relations of electrocardiograms. *Heart*, 7, 353–370.

See also the [ECG Feature Review](ecg_features_review.md).
