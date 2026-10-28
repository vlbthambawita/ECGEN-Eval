# Metric Reference

Definitions, constructor parameters and `extra` contents for every metric. Notation:
\(X^{r}\) is the set of real recordings, \(X^{s}\) the synthetic set, and all per-lead scores
are averaged to give the overall `score` unless stated otherwise.
For intuition and interactive demos, see [Metrics Explained](../metrics/index.md).

Each metric section links to three places:
:material-school: its **Metrics Explained** page,
:material-api: its **API** entry, and
:material-github: its **source code** on GitHub.
The **Reference** line links to the paper that defines the metric.

## At a glance

| Metric | Family | Better | Range | Explained | Source |
|---|---|:---:|---|---|---|
| [`mmd`](#mmd) | Distribution | ↓ | \(\ge 0\) | [MMD](../metrics/mmd.md) | [`mmd.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/mmd.py) |
| [`fd`](#fd) | Distribution | ↓ | \(\ge 0\) | [FD](../metrics/fd.md) | [`fd.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/fd.py) |
| [`fed`](#fed) | Distribution | ↓ | \(\ge 0\) | [FED](../metrics/fed.md) | [`fed.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/fed.py) |
| [`swd`](#swd) | Distribution | ↓ | \(\ge 0\) | [SWD](../metrics/swd.md) | [`swd.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/swd.py) |
| [`pr_dist`](#pr_dist) | Distribution | ↑ | \([0, 1]\) | [Precision & Recall](../metrics/pr_dist.md) | [`pr_dist.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/pr_dist.py) |
| [`prd`](#prd) | Signal fidelity | ↓ | \(\ge 0\) (%) | [PRD](../metrics/prd.md) | [`prd.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/prd.py) |
| [`mae`](#mae) | Signal fidelity | ↓ | \(\ge 0\) (signal units) | [MAE](../metrics/mae.md) | [`mae.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/mae.py) |
| [`psnr`](#psnr) | Signal fidelity | ↑ | dB, capped at 100 | [PSNR](../metrics/psnr.md) | [`psnr.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/psnr.py) |
| [`ssim`](#ssim) | Signal fidelity | ↑ | \([-1, 1]\) | [SSIM](../metrics/ssim.md) | [`ssim.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/ssim.py) |
| [`dtw`](#dtw) | Signal fidelity | ↓ | \(\ge 0\) | [DTW](../metrics/dtw.md) | [`dtw.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/dtw.py) |
| [`sqi`](#sqi) | Morphology | ↑ | \([-1, 1]\) | [SQI](../metrics/sqi.md) | [`sqi.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/sqi.py) |
| [`psd`](#psd) | Spectral | ↓ | \([0, \ln 2]\) | [PSD](../metrics/psd.md) | [`psd.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/psd.py) |
| [`spectral_entropy`](#spectral_entropy) | Spectral | ↓ | \([0, \ln 2]\) | [Spectral entropy](../metrics/spectral_entropy.md) | [`spectral_entropy.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/spectral_entropy.py) |
| [`heart_rate`](#heart_rate) | Physiological | ↓ | \([0, \ln 2]\) | [Heart rate](../metrics/heart_rate.md) | [`heart_rate.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/heart_rate.py) |
| [`hrv`](#hrv) | Physiological | ↓ | \([0, \ln 2]\) | [HRV](../metrics/hrv.md) | [`hrv.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/hrv.py) |
| [`nn_dist`](#nn_dist) | Privacy | ↓ | \(\ge 0\) | [NN distance](../metrics/nn_dist.md) | [`nn_dist.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/nn_dist.py) |

## Shared building blocks

**7-feature signal descriptor.** Used by `mmd`, `swd`, `pr_dist` and `nn_dist`. It is computed
per lead and per recording: mean, standard deviation, RMS, maximum absolute amplitude, energy
(\(\sum x^2 / T\)), zero-crossing rate and lag-1 autocorrelation.

**Feature scaling.** Before distances are computed, the descriptors are scaled with statistics
of the **real** set only, so a synthetic set cannot change the scale it is judged on:

| Metric | Scaling |
|---|---|
| `fd` | z-score: subtract the real mean, divide by the real standard deviation |
| `swd`, `pr_dist`, `nn_dist` | divide by the real standard deviation |
| `mmd` | none; the kernel bandwidth adapts through the median heuristic |

**Histogram Jensen–Shannon divergence.** `spectral_entropy`, `heart_rate` and `hrv` turn one
scalar per recording into two histograms. Each histogram has 50 equal bins spanning the pooled
real and synthetic range. The score is the JS divergence between them, using the natural log
and clipped to \([0, \ln 2]\). `psd` uses the same divergence, applied to the mean spectra.

---

## Distribution metrics

### `mmd` — Maximum Mean Discrepancy { #mmd }

:material-school: [Explained](../metrics/mmd.md) ·
:material-api: [`MMDMetric`](../api/metrics.md#ecgen_eval.metrics.mmd.MMDMetric) ·
:material-github: [`mmd.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/mmd.py)

Kernel two-sample statistic between the distributions of the 7-feature descriptors.

\[
\mathrm{MMD}^2 = \mathbb{E}[k(x,x')] + \mathbb{E}[k(y,y')] - 2\,\mathbb{E}[k(x,y)]
\]

The kernel is a multi-scale RBF. Its bandwidths are multiples of the median pairwise squared
distance. Negative estimates are clipped to 0.

| Parameter | Default | Description |
|---|---|---|
| `kernel_bandwidths` | `[0.1, 1.0, 10.0]` | Multipliers of the median heuristic |
| `n_subsample` | `1000` | Max recordings per set |

`extra`: `per_lead_mmd2`.

**Reference:** Gretton et al. (2012). A kernel two-sample test. *JMLR* 13, 723–773.
[jmlr.org](https://jmlr.org/papers/v13/gretton12a.html)

### `fd` — Fréchet Distance { #fd }

:material-school: [Explained](../metrics/fd.md) ·
:material-api: [`FDMetric`](../api/metrics.md#ecgen_eval.metrics.fd.FDMetric) ·
:material-github: [`fd.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/fd.py)

FID-style distance between Gaussians fitted to an **11-feature** descriptor per lead. The
features are mean, std, skewness, kurtosis, RMS, energy, max |x|, zero-crossing rate, lag-1
autocorrelation, spectral centroid and spectral bandwidth. They are z-scored with the real-set
statistics before fitting.

\[
\mathrm{FD} = \lVert \mu_r - \mu_s \rVert^2 + \operatorname{Tr}\!\left(\Sigma_r + \Sigma_s - 2(\Sigma_r\Sigma_s)^{1/2}\right)
\]

| Parameter | Default | Description |
|---|---|---|
| `n_subsample` | `2000` | Max recordings per set |
| `eps` | `1e-6` | Diagonal regulariser for the matrix square root |

**Reference:** Heusel et al. (2017). GANs trained by a two time-scale update rule converge to a
local Nash equilibrium. *NeurIPS* 30. [arXiv:1706.08500](https://arxiv.org/abs/1706.08500).
Applied to ECG in Thambawita et al. (2021), *Sci Rep* 11, 21896.
[doi:10.1038/s41598-021-01295-2](https://doi.org/10.1038/s41598-021-01295-2)

### `fed` — Fréchet ECG Distance { #fed }

:material-school: [Explained](../metrics/fed.md) ·
:material-api: [`FEDMetric`](../api/metrics.md#ecgen_eval.metrics.fed.FEDMetric) ·
:material-github: [`fed.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/fed.py)

Same formula as `fd`, applied to whole-recording embeddings from a pre-trained ECG foundation
model. There are no per-lead scores. The encoder adapters live in
[`ecgen_eval/metrics/encoders/`](https://github.com/vlbthambawita/ECGEN-Eval/tree/main/ecgen_eval/metrics/encoders)
(see the [FED Encoders API](../api/encoders.md)).

| Parameter | Default | Description |
|---|---|---|
| `backbone` | `"ecgfounder"` | `ecgfounder`, `hubert_ecg` or `ecgfm` |
| `device` | `"cpu"` | PyTorch device |
| `batch_size` | `32` | Recordings per forward pass |
| `n_subsample` | `None` | Optional cap on recordings |
| `eps` | `1e-6` | Diagonal regulariser |

`extra`: `backbone`.

**Reference:** Heusel et al. (2017), [arXiv:1706.08500](https://arxiv.org/abs/1706.08500).
The embedding-based variant follows Kilgour et al. (2019), Fréchet Audio Distance,
[arXiv:1812.08466](https://arxiv.org/abs/1812.08466).
Backbone papers are listed under [References](../references.md#foundation-models-fed-backbones).

### `swd` — Sliced Wasserstein Distance { #swd }

:material-school: [Explained](../metrics/swd.md) ·
:material-api: [`SWDMetric`](../api/metrics.md#ecgen_eval.metrics.swd.SWDMetric) ·
:material-github: [`swd.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/swd.py)

The 7-feature descriptors are scaled by the real standard deviation and projected onto
`n_projections` random unit directions. The score is the mean, over projections, of the exact
1-D Wasserstein-1 distance (sorted quantile matching).

| Parameter | Default | Description |
|---|---|---|
| `n_projections` | `200` | Random projection directions |
| `n_subsample` | `1000` | Max recordings per set |
| `seed` | `42` | RNG seed |

**Reference:** Rabin et al. (2011). Wasserstein barycenter and its application to texture
mixing. *SSVM*, LNCS 6667.
[doi:10.1007/978-3-642-24785-9_37](https://doi.org/10.1007/978-3-642-24785-9_37).
Kolouri et al. (2019). Generalized sliced Wasserstein distances. *NeurIPS* 32.
[arXiv:1902.00434](https://arxiv.org/abs/1902.00434)

### `pr_dist` — Precision & Recall { #pr_dist }

:material-school: [Explained](../metrics/pr_dist.md) ·
:material-api: [`PRDistMetric`](../api/metrics.md#ecgen_eval.metrics.pr_dist.PRDistMetric) ·
:material-github: [`pr_dist.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/pr_dist.py)

k-NN manifold estimate on the 7-feature descriptors, scaled by the real standard deviation.

- **Precision** — the fraction of synthetic samples that fall inside the real manifold, that
  is, within the k-th-NN radius of some real sample.
- **Recall** — the fraction of real samples that fall inside the synthetic manifold.

The score is their harmonic mean (F-score), in \([0, 1]\), **higher is better**.

| Parameter | Default | Description |
|---|---|---|
| `k` | `3` | Neighbour index for the manifold radius |
| `n_subsample` | `1000` | Max recordings per set |
| `seed` | `42` | RNG seed |

`extra`: `precision`, `recall` (per-lead dicts).

**Reference:** Kynkäänniemi et al. (2019). Improved precision and recall metric for assessing
generative models. *NeurIPS* 32. [arXiv:1904.06991](https://arxiv.org/abs/1904.06991)

---

## Signal-fidelity metrics

`prd`, `mae`, `psnr` and `ssim` are **unpaired**. Each real recording is compared with its
nearest synthetic neighbour (minimum Euclidean distance), and the error of that pair is
averaged. The neighbour is chosen in one of two ways:

| Metric | Neighbour chosen |
|---|---|
| `prd` | Once per real recording, using **all leads jointly**. Every lead is then scored against the same synthetic recording. |
| `mae`, `psnr`, `ssim` | **Separately for each lead**. Lead I and lead II of one real recording may be matched to different synthetic recordings, which makes these scores more forgiving. |

`dtw` is different: it compares randomly drawn pairs, not nearest neighbours.

### `prd` — Percent Root-mean-square Difference { #prd }

:material-school: [Explained](../metrics/prd.md) ·
:material-api: [`PRDMetric`](../api/metrics.md#ecgen_eval.metrics.prd.PRDMetric) ·
:material-github: [`prd.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/prd.py)

\[
\mathrm{PRD} = 100 \cdot \frac{\lVert x_r - x_s \rVert_2}{\lVert x_r \rVert_2}
\]

The nearest neighbour is chosen on all leads jointly; PRD is then computed per lead.

| Parameter | Default |
|---|---|
| `n_subsample` | `500` |
| `seed` | `42` |

**Reference:** Zigel, Cohen & Katz (2000). The weighted diagnostic distortion (WDD) measure for
ECG signal compression. *IEEE TBME* 47(11), 1422–1430.
[doi:10.1109/TBME.2000.880093](https://doi.org/10.1109/TBME.2000.880093)

### `mae` — Mean Absolute Error { #mae }

:material-school: [Explained](../metrics/mae.md) ·
:material-api: [`MAEMetric`](../api/metrics.md#ecgen_eval.metrics.mae.MAEMetric) ·
:material-github: [`mae.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/mae.py)

MAE per lead, against the nearest synthetic neighbour **of that lead**. RMSE to the same
neighbour is reported alongside.

| Parameter | Default |
|---|---|
| `n_subsample` | `500` |
| `seed` | `42` |

`extra`: `per_lead_rmse`, `rmse`.

**Reference:** Zigel, Cohen & Katz (2000), *IEEE TBME*.
[doi:10.1109/TBME.2000.880093](https://doi.org/10.1109/TBME.2000.880093).
Applied to synthetic ECG in Thambawita et al. (2021).
[doi:10.1038/s41598-021-01295-2](https://doi.org/10.1038/s41598-021-01295-2)

### `psnr` — Peak Signal-to-Noise Ratio { #psnr }

:material-school: [Explained](../metrics/psnr.md) ·
:material-api: [`PSNRMetric`](../api/metrics.md#ecgen_eval.metrics.psnr.PSNRMetric) ·
:material-github: [`psnr.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/psnr.py)

\[
\mathrm{PSNR} = 10 \log_{10} \frac{\mathrm{MAX}^2}{\mathrm{MSE}}
\]

MAX is the peak-to-peak amplitude of the real signal, and MSE is computed against the nearest
synthetic neighbour of the same lead. Identical or flat signals score 100 dB. Higher is better.

| Parameter | Default |
|---|---|
| `n_subsample` | `500` |
| `seed` | `42` |

**Reference:** Huynh-Thu & Ghanbari (2008). Scope of validity of PSNR in image/video quality
assessment. *Electronics Letters* 44(13), 800–801.
[doi:10.1049/el:20080522](https://doi.org/10.1049/el:20080522)

### `ssim` — Structural Similarity (1-D) { #ssim }

:material-school: [Explained](../metrics/ssim.md) ·
:material-api: [`SSIMMetric`](../api/metrics.md#ecgen_eval.metrics.ssim.SSIMMetric) ·
:material-github: [`ssim.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/ssim.py)

Global (non-windowed) SSIM between each real signal and the nearest synthetic neighbour of the
same lead:

\[
\mathrm{SSIM}(x,y) = \frac{(2\mu_x\mu_y + C_1)(2\sigma_{xy} + C_2)}{(\mu_x^2 + \mu_y^2 + C_1)(\sigma_x^2 + \sigma_y^2 + C_2)}
\]

Here \(C_i = (k_i L)^2\) and \(L\) is the dynamic range of the real signal. Range
\([-1, 1]\), **higher is better**.

| Parameter | Default |
|---|---|
| `k1` | `0.01` |
| `k2` | `0.03` |
| `n_subsample` | `500` |
| `seed` | `42` |

**Reference:** Wang et al. (2004). Image quality assessment: from error visibility to structural
similarity. *IEEE TIP* 13(4), 600–612.
[doi:10.1109/TIP.2003.819861](https://doi.org/10.1109/TIP.2003.819861).
Applied to ECG signal quality in Shahriari et al. (2018), *IEEE TBME* 65(4), 745–753.
[doi:10.1109/TBME.2017.2717876](https://doi.org/10.1109/TBME.2017.2717876)

### `dtw` — Dynamic Time Warping { #dtw }

:material-school: [Explained](../metrics/dtw.md) ·
:material-api: [`DTWMetric`](../api/metrics.md#ecgen_eval.metrics.dtw.DTWMetric) ·
:material-github: [`dtw.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/dtw.py)

Mean DTW distance over `n_pairs` randomly drawn (real, synthetic) pairs, computed per lead.
The signals are first downsampled by `downsample`, and the warping is limited to a Sakoe–Chiba
band of `window × length`. The fast `dtaidistance` C implementation is used when available,
with a pure-NumPy fallback otherwise.

| Parameter | Default | Description |
|---|---|---|
| `n_pairs` | `200` | Random pairs evaluated |
| `downsample` | `5` | Temporal stride before DTW |
| `window` | `0.1` | Band width as a fraction of length |
| `seed` | `42` | RNG seed |

`extra`: `per_lead_dtw`, `per_lead_all_distances` (used for the violin plot in the report),
`n_pairs`, `downsample_factor`, `window_fraction`.

**Reference:** Berndt & Clifford (1994). Using dynamic time warping to find patterns in time
series. *AAAI KDD Workshop*, 359–370.
[PDF](https://cdn.aaai.org/Workshops/1994/WS-94-03/WS94-03-031.pdf)

---

## Morphology

### `sqi` — Signal Quality Index { #sqi }

:material-school: [Explained](../metrics/sqi.md) ·
:material-api: [`SQIMetric`](../api/metrics.md#ecgen_eval.metrics.sqi.SQIMetric) ·
:material-github: [`sqi.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/sqi.py)

1. Each recording is amplitude-normalised to zero mean and unit range.
2. A per-lead template is built as the mean of the normalised real recordings.
3. The score is the mean Pearson correlation between each normalised synthetic recording and
   the template.

Range \([-1, 1]\), **higher is better**.

`extra["real_self_sqi"]` gives the same statistic for the real recordings against their own
template — a useful ceiling to compare against.

| Parameter | Default |
|---|---|
| `n_subsample` | `1000` |
| `seed` | `42` |

**Reference:** Clifford et al. (2017). AF classification from a short single lead ECG
recording: the PhysioNet/Computing in Cardiology Challenge 2017. *CinC* 44.
[doi:10.22489/CinC.2017.065-469](https://doi.org/10.22489/CinC.2017.065-469)

---

## Spectral metrics

### `psd` — Power Spectral Density divergence { #psd }

:material-school: [Explained](../metrics/psd.md) ·
:material-api: [`PSDMetric`](../api/metrics.md#ecgen_eval.metrics.psd.PSDMetric) ·
:material-github: [`psd.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/psd.py)

1. PSD of every signal per lead (Welch via SciPy, plain FFT otherwise).
2. Mean PSD across the real set and across the synthetic set, each normalised to sum to 1.
3. Jensen–Shannon divergence between the two, in \([0, \ln 2]\).

| Parameter | Default | Description |
|---|---|---|
| `fs` | `500.0` | Sampling rate in Hz |
| `nperseg` | `None` | Welch segment length (auto) |
| `n_subsample` | `1000` | Max recordings per set |

`extra`: `per_lead_psd_real`, `per_lead_psd_synth` (mean PSD curves, used for the PSD overlay plot).

**Reference:** Welch (1967). The use of fast Fourier transform for the estimation of power
spectra. *IEEE Trans. Audio Electroacoust.* 15(2), 70–73.
[doi:10.1109/TAU.1967.1161901](https://doi.org/10.1109/TAU.1967.1161901).
Applied to synthetic ECG in Golany & Radinsky (2019), *AAAI* 33.
[doi:10.1609/aaai.v33i01.3301557](https://doi.org/10.1609/aaai.v33i01.3301557)

### `spectral_entropy` — Spectral Entropy divergence { #spectral_entropy }

:material-school: [Explained](../metrics/spectral_entropy.md) ·
:material-api: [`SpectralEntropyMetric`](../api/metrics.md#ecgen_eval.metrics.spectral_entropy.SpectralEntropyMetric) ·
:material-github: [`spectral_entropy.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/spectral_entropy.py)

Each recording's spectral entropy is the Shannon entropy of its normalised PSD,
\(\mathrm{SE} = -\sum_f p(f)\log_2 p(f)\). The score is the
[histogram JS divergence](#shared-building-blocks) between the real and synthetic entropy
distributions.

| Parameter | Default |
|---|---|
| `fs` | `500.0` |
| `nperseg` | `None` (min(256, T)) |
| `n_subsample` | `1000` |
| `seed` | `42` |

`extra[lead]`: `real_se_mean`, `real_se_std`, `synth_se_mean`, `synth_se_std`.

**Reference:** Inouye et al. (1991). Quantification of EEG irregularity by use of the entropy
of the power spectrum. *EEG Clin. Neurophysiol.* 79(3), 204–210.
[doi:10.1016/0013-4694(91)90138-T](https://doi.org/10.1016/0013-4694(91)90138-T)

---

## Physiological metrics

Both metrics detect R-peaks per lead with a slope-energy QRS detector in the spirit of
Pan–Tompkins. The detector band-passes at 5–15 Hz, squares the derivative, integrates over
120 ms and applies a 0.2 s refractory period, so it handles heart rates up to 300 bpm. SciPy
`find_peaks` is used when available, with a NumPy fallback. The detector is in
[`_rpeaks.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/_rpeaks.py).

The resulting distributions are compared with the
[histogram JS divergence](#shared-building-blocks).

!!! warning "Recordings where no rhythm is detected are skipped"
    A recording is dropped (it becomes NaN) when too few R-peaks are found:

    - `heart_rate` needs at least 2 peaks.
    - `hrv` needs at least 3 peaks (2 RR intervals).

    If **every** recording of one set is dropped for a lead, the score for that lead is
    reported as **0**, which looks like a perfect match. Check `synth_hr_mean` (or
    `synth_sdnn_mean`) in `extra`: a NaN there means no beats were found.

### `heart_rate` — Heart-rate distribution { #heart_rate }

:material-school: [Explained](../metrics/heart_rate.md) ·
:material-api: [`HeartRateMetric`](../api/metrics.md#ecgen_eval.metrics.heart_rate.HeartRateMetric) ·
:material-github: [`heart_rate.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/heart_rate.py)

HR = 60 / mean(RR) per recording; score = JS divergence between real and synthetic HR
distributions.

| Parameter | Default |
|---|---|
| `fs` | `500.0` |
| `n_subsample` | `1000` |
| `seed` | `42` |

`extra[lead]`: `real_hr_mean`, `real_hr_std`, `synth_hr_mean`, `synth_hr_std`.

**Reference:** Pan & Tompkins (1985). A real-time QRS detection algorithm. *IEEE TBME* 32(3),
230–236. [doi:10.1109/TBME.1985.325532](https://doi.org/10.1109/TBME.1985.325532)

### `hrv` — Heart-rate variability { #hrv }

:material-school: [Explained](../metrics/hrv.md) ·
:material-api: [`HRVMetric`](../api/metrics.md#ecgen_eval.metrics.hrv.HRVMetric) ·
:material-github: [`hrv.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/hrv.py)

Per recording: SDNN (sample standard deviation of RR, in ms), rMSSD (in ms) and pNN50 (a
fraction in \([0, 1]\)). For each lead, the score is the mean of the three JS divergences
between the real and synthetic distributions.

| Parameter | Default |
|---|---|
| `fs` | `500.0` |
| `n_subsample` | `1000` |
| `seed` | `42` |

`extra[lead]`: `real_sdnn_mean`, `synth_sdnn_mean`, `real_rmssd_mean`, `synth_rmssd_mean`,
`real_pnn50_mean`, `synth_pnn50_mean`.

**Reference:** Task Force of the ESC and NASPE (1996). Heart rate variability: standards of
measurement, physiological interpretation, and clinical use. *Circulation* 93(5), 1043–1065.
[doi:10.1161/01.CIR.93.5.1043](https://doi.org/10.1161/01.CIR.93.5.1043)

!!! note
    Short recordings (e.g. 10 s) contain only a handful of beats, so HRV statistics are noisy.
    Interpret `hrv` on short strips with care.

---

## Privacy

### `nn_dist` — Nearest-Neighbour Distance { #nn_dist }

:material-school: [Explained](../metrics/nn_dist.md) ·
:material-api: [`NNDistMetric`](../api/metrics.md#ecgen_eval.metrics.nn_dist.NNDistMetric) ·
:material-github: [`nn_dist.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/nn_dist.py)

Computed on the 7-feature descriptors, scaled by the real standard deviation:

- **score** — mean distance from each real recording to its nearest synthetic recording.
- **authenticity** (`extra["authenticity"]`, per lead) — the fraction of synthetic recordings
  whose nearest-real distance exceeds the median real-to-real nearest-neighbour distance.
  Low authenticity suggests the generator produces near-copies of real data.

| Parameter | Default |
|---|---|
| `n_subsample` | `1000` |
| `seed` | `42` |

**Reference:** Meehan, Chaudhuri & Dasgupta (2020). A non-parametric test to detect data-copying
in generative models. *AISTATS*. [arXiv:2004.05675](https://arxiv.org/abs/2004.05675)
