# Metric Reference

Definitions, constructor parameters and `extra` contents for every metric. Notation:
\(X^{r}\) is the set of real recordings, \(X^{s}\) the synthetic set, and all per-lead scores
are averaged to give the overall `score` unless stated otherwise.
For intuition and interactive demos, see [Metrics Explained](../metrics/index.md).

Several metrics share a compact **7-feature signal descriptor** computed per lead and per
recording: mean, standard deviation, RMS, maximum absolute amplitude, energy
(\(\sum x^2 / T\)), zero-crossing rate and lag-1 autocorrelation. It is used by `mmd`, `swd`,
`pr_dist` and `nn_dist`.

---

## Distribution metrics

### `mmd` — Maximum Mean Discrepancy { #mmd }

Kernel two-sample statistic between the distributions of the 7-feature descriptors.

\[
\mathrm{MMD}^2 = \mathbb{E}[k(x,x')] + \mathbb{E}[k(y,y')] - 2\,\mathbb{E}[k(x,y)]
\]

with a multi-scale RBF kernel whose bandwidths are multiples of the median pairwise distance.
Negative estimates are clipped to 0.

| Parameter | Default | Description |
|---|---|---|
| `kernel_bandwidths` | `[0.1, 1.0, 10.0]` | Multipliers of the median heuristic |
| `n_subsample` | `1000` | Max recordings per set |

`extra`: `per_lead_mmd2`.
Reference: Gretton et al., *JMLR* 13, 2012.

### `fd` — Fréchet Distance { #fd }

FID-style distance between Gaussians fitted to an **11-feature** descriptor per lead
(mean, std, skewness, kurtosis, RMS, energy, max |x|, zero-crossing rate, lag-1
autocorrelation, spectral centroid, spectral bandwidth), z-scored before fitting.

\[
\mathrm{FD} = \lVert \mu_r - \mu_s \rVert^2 + \operatorname{Tr}\!\left(\Sigma_r + \Sigma_s - 2(\Sigma_r\Sigma_s)^{1/2}\right)
\]

| Parameter | Default | Description |
|---|---|---|
| `n_subsample` | `2000` | Max recordings per set |
| `eps` | `1e-6` | Diagonal regulariser for the matrix square root |

Reference: Heusel et al., *NeurIPS* 2017; applied to ECG in Thambawita et al., *Sci Rep* 2021.

### `fed` — Fréchet ECG Distance { #fed }

Same formula as `fd`, but on whole-recording embeddings from a pre-trained ECG foundation
model. No per-lead scores. See the dedicated [FED page](../metrics/fed.md).

| Parameter | Default | Description |
|---|---|---|
| `backbone` | `"ecgfounder"` | `ecgfounder`, `hubert_ecg` or `ecgfm` |
| `device` | `"cpu"` | PyTorch device |
| `batch_size` | `32` | Recordings per forward pass |
| `n_subsample` | `None` | Optional cap on recordings |
| `eps` | `1e-6` | Diagonal regulariser |

`extra`: `backbone`.

### `swd` — Sliced Wasserstein Distance { #swd }

Projects the 7-feature descriptors onto `n_projections` random unit directions and averages
the exact 1-D Wasserstein-1 distance (sorted quantile matching) over projections.

| Parameter | Default | Description |
|---|---|---|
| `n_projections` | `200` | Random projection directions |
| `n_subsample` | `1000` | Max recordings per set |
| `seed` | `42` | RNG seed |

Reference: Rabin et al., 2011; Kolouri et al., *NeurIPS* 2019.

### `pr_dist` — Precision & Recall { #pr_dist }

k-NN manifold estimate on the 7-feature descriptors (Kynkäänniemi et al., 2019).

- **Precision** — fraction of synthetic samples that fall inside the real manifold
  (within the k-th-NN radius of some real sample).
- **Recall** — fraction of real samples that fall inside the synthetic manifold.

The score is their harmonic mean (F-score), in \([0, 1]\), **higher is better**.

| Parameter | Default | Description |
|---|---|---|
| `k` | `3` | Neighbour index for the manifold radius |
| `n_subsample` | `1000` | Max recordings per set |
| `seed` | `42` | RNG seed |

`extra`: `precision`, `recall` (per-lead dicts).

---

## Signal-fidelity metrics

The nearest-neighbour metrics below match **each real recording to its nearest synthetic
recording** (minimum Euclidean distance), then measure the error of that pair.

### `prd` — Percent Root-mean-square Difference { #prd }

\[
\mathrm{PRD} = 100 \cdot \frac{\lVert x_r - x_s \rVert_2}{\lVert x_r \rVert_2}
\]

The nearest neighbour is chosen on all leads jointly; PRD is then computed per lead.

| Parameter | Default |
|---|---|
| `n_subsample` | `500` |
| `seed` | `42` |

Reference: Zigel et al., *IEEE TBME* 2000.

### `mae` — Mean Absolute Error { #mae }

Per-lead MAE to the nearest synthetic neighbour; RMSE is reported alongside.

| Parameter | Default |
|---|---|
| `n_subsample` | `500` |
| `seed` | `42` |

`extra`: `per_lead_rmse`, `rmse`.

### `psnr` — Peak Signal-to-Noise Ratio { #psnr }

\[
\mathrm{PSNR} = 10 \log_{10} \frac{\mathrm{MAX}^2}{\mathrm{MSE}}
\]

with MAX the peak-to-peak amplitude of the real signal. In dB, **higher is better**.

| Parameter | Default |
|---|---|
| `n_subsample` | `500` |
| `seed` | `42` |

Reference: Huynh-Thu & Ghanbari, *Electron. Lett.* 2008.

### `ssim` — Structural Similarity (1-D) { #ssim }

Global (non-windowed) SSIM between each real signal and its nearest synthetic neighbour:

\[
\mathrm{SSIM}(x,y) = \frac{(2\mu_x\mu_y + C_1)(2\sigma_{xy} + C_2)}{(\mu_x^2 + \mu_y^2 + C_1)(\sigma_x^2 + \sigma_y^2 + C_2)}
\]

with \(C_i = (k_i L)^2\) and \(L\) the dynamic range of the real signal. Range \([-1, 1]\),
**higher is better**.

| Parameter | Default |
|---|---|
| `k1` | `0.01` |
| `k2` | `0.03` |
| `n_subsample` | `500` |
| `seed` | `42` |

Reference: Wang et al., *IEEE TIP* 2004; Hayn et al., *Physiol. Meas.* 2018.

### `dtw` — Dynamic Time Warping { #dtw }

Mean DTW distance over `n_pairs` randomly drawn (real, synthetic) pairs, computed per lead on
signals downsampled by `downsample`, with a Sakoe–Chiba band of `window × length`. Uses the
fast `dtaidistance` C implementation when available and a pure-NumPy fallback otherwise.

| Parameter | Default | Description |
|---|---|---|
| `n_pairs` | `200` | Random pairs evaluated |
| `downsample` | `5` | Temporal stride before DTW |
| `window` | `0.1` | Band width as a fraction of length |
| `seed` | `42` | RNG seed |

`extra`: `per_lead_dtw`, `per_lead_all_distances` (used for the violin plot in the report),
`n_pairs`, `downsample_factor`, `window_fraction`.
Reference: Berndt & Clifford, *KDD Workshop* 1994.

---

## Morphology

### `sqi` — Signal Quality Index { #sqi }

Builds a per-lead template as the mean of the amplitude-normalised real recordings and reports
the mean Pearson correlation between each synthetic recording and the template. Range
\([-1, 1]\), **higher is better**.

`extra["real_self_sqi"]` gives the same statistic for the real recordings against their own
template — a useful ceiling to compare against.

| Parameter | Default |
|---|---|
| `n_subsample` | `1000` |
| `seed` | `42` |

---

## Spectral metrics

### `psd` — Power Spectral Density divergence { #psd }

1. PSD of every signal per lead (Welch via SciPy, plain FFT otherwise).
2. Mean PSD across the real set and across the synthetic set, each normalised to sum to 1.
3. Jensen–Shannon divergence between the two, in \([0, \ln 2]\).

| Parameter | Default | Description |
|---|---|---|
| `fs` | `500.0` | Sampling rate in Hz |
| `nperseg` | `None` | Welch segment length (auto) |
| `n_subsample` | `1000` | Max recordings per set |

`extra`: `per_lead_psd_real`, `per_lead_psd_synth` (mean PSD curves, used for the PSD overlay plot).
Reference: Welch, 1967; Golany & Radinsky, *AAAI* 2019.

### `spectral_entropy` — Spectral Entropy divergence { #spectral_entropy }

Shannon entropy of each recording's normalised PSD,
\(\mathrm{SE} = -\sum_f p(f)\log_2 p(f)\), then the JS divergence between the real and
synthetic entropy distributions (50-bin histograms).

| Parameter | Default |
|---|---|
| `fs` | `500.0` |
| `nperseg` | `None` (min(256, T)) |
| `n_subsample` | `1000` |
| `seed` | `42` |

`extra[lead]`: `real_se_mean`, `real_se_std`, `synth_se_mean`, `synth_se_std`.

---

## Physiological metrics

Both metrics detect R-peaks per lead with a slope-energy QRS detector in the spirit of
Pan–Tompkins (5–15 Hz band-pass, squared derivative, 120 ms integration, 0.2 s refractory
period, so heart rates up to 300 bpm), then compare histogram distributions with the
Jensen–Shannon divergence. SciPy `find_peaks` is used when available, with a NumPy fallback.

### `heart_rate` — Heart-rate distribution { #heart_rate }

HR = 60 / mean(RR) per recording; score = JS divergence between real and synthetic HR
distributions.

| Parameter | Default |
|---|---|
| `fs` | `500.0` |
| `n_subsample` | `1000` |
| `seed` | `42` |

`extra[lead]`: `real_hr_mean`, `real_hr_std`, `synth_hr_mean`, `synth_hr_std`.
Reference: Pan & Tompkins, *IEEE TBME* 1985.

### `hrv` — Heart-rate variability { #hrv }

Per recording: SDNN, rMSSD and pNN50. Per lead, the score is the mean of the three JS
divergences between real and synthetic distributions.

| Parameter | Default |
|---|---|
| `fs` | `500.0` |
| `n_subsample` | `1000` |
| `seed` | `42` |

`extra[lead]`: `real_sdnn_mean`, `synth_sdnn_mean`, `real_rmssd_mean`, `synth_rmssd_mean`,
`real_pnn50_mean`, `synth_pnn50_mean`.
Reference: Task Force ESC/NASPE, *Circulation* 1996.

!!! note
    Short recordings (e.g. 10 s) contain only a handful of beats, so HRV statistics are noisy.
    Interpret `hrv` on short strips with care.

---

## Privacy

### `nn_dist` — Nearest-Neighbour Distance { #nn_dist }

On the 7-feature descriptors (scaled by the real standard deviation):

- **score** — mean distance from each real recording to its nearest synthetic recording.
- **authenticity** (`extra["authenticity"]`, per lead) — fraction of synthetic recordings
  whose nearest-real distance exceeds the median real-to-real nearest-neighbour distance.
  Low authenticity suggests the generator produces near-copies of real data.

| Parameter | Default |
|---|---|
| `n_subsample` | `1000` |
| `seed` | `42` |

Reference: Meehan et al., *AISTATS* 2020.
