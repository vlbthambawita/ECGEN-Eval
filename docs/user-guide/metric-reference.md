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
| [`js_div`](#js_div) | Distribution | ↓ | \([0, \ln 2]\) | [Amplitude JS / KL](../metrics/js_div.md) | [`js_div.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/js_div.py) |
| [`ks_test`](#ks_test) | Distribution | ↓ | \([0, 1]\) | [KS test](../metrics/ks_test.md) | [`ks_test.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/ks_test.py) |
| [`c2st`](#c2st) | Distribution | ↓ | \([0, 0.5]\) | [C2ST](../metrics/c2st.md) | [`c2st.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/c2st.py) |
| [`prd`](#prd) | Signal fidelity | ↓ | \(\ge 0\) (%) | [PRD](../metrics/prd.md) | [`prd.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/prd.py) |
| [`mae`](#mae) | Signal fidelity | ↓ | \(\ge 0\) (signal units) | [MAE](../metrics/mae.md) | [`mae.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/mae.py) |
| [`psnr`](#psnr) | Signal fidelity | ↑ | dB, capped at 100 | [PSNR](../metrics/psnr.md) | [`psnr.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/psnr.py) |
| [`ssim`](#ssim) | Signal fidelity | ↑ | \([-1, 1]\) | [SSIM](../metrics/ssim.md) | [`ssim.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/ssim.py) |
| [`dtw`](#dtw) | Signal fidelity | ↓ | \(\ge 0\) | [DTW](../metrics/dtw.md) | [`dtw.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/dtw.py) |
| [`mse`](#mse) | Signal fidelity | ↓ | \(\ge 0\) (signal units²) | [MSE](../metrics/mse.md) | [`mse.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/mse.py) |
| [`rmse`](#rmse) | Signal fidelity | ↓ | \(\ge 0\) (signal units) | [RMSE](../metrics/mse.md) | [`mse.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/mse.py) |
| [`euclidean`](#euclidean) | Signal fidelity | ↓ | \(\ge 0\) (signal units) | [Euclidean](../metrics/euclidean.md) | [`euclidean.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/euclidean.py) |
| [`pearson`](#pearson) | Signal fidelity | ↑ | \([-1, 1]\) | [Pearson](../metrics/pearson.md) | [`pearson.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/pearson.py) |
| [`cosine`](#cosine) | Signal fidelity | ↑ | \([-1, 1]\) | [Cosine](../metrics/cosine.md) | [`cosine.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/cosine.py) |
| [`curve_frechet`](#curve_frechet) | Signal fidelity | ↓ | \(\ge 0\) (signal units) | [Curve Fréchet](../metrics/curve_frechet.md) | [`curve_frechet.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/curve_frechet.py) |
| [`sqi`](#sqi) | Morphology | ↑ | \([-1, 1]\) | [SQI](../metrics/sqi.md) | [`sqi.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/sqi.py) |
| [`psd`](#psd) | Spectral | ↓ | \([0, \ln 2]\) | [PSD](../metrics/psd.md) | [`psd.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/psd.py) |
| [`spectral_entropy`](#spectral_entropy) | Spectral | ↓ | \([0, \ln 2]\) | [Spectral entropy](../metrics/spectral_entropy.md) | [`spectral_entropy.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/spectral_entropy.py) |
| [`heart_rate`](#heart_rate) | Physiological | ↓ | \([0, \ln 2]\) | [Heart rate](../metrics/heart_rate.md) | [`heart_rate.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/heart_rate.py) |
| [`hrv`](#hrv) | Physiological | ↓ | \([0, \ln 2]\) | [HRV](../metrics/hrv.md) | [`hrv.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/hrv.py) |
| [`nn_dist`](#nn_dist) | Privacy | ↓ | \(\ge 0\) | [NN distance](../metrics/nn_dist.md) | [`nn_dist.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/nn_dist.py) |

## Shared building blocks

**7-feature signal descriptor.** Used by `mmd`, `swd`, `pr_dist`, `nn_dist` and `ks_test`. It
is computed per lead and per recording: mean, standard deviation, RMS, maximum absolute
amplitude, energy (\(\sum x^2 / T\)), zero-crossing rate and lag-1 autocorrelation.

**11-feature signal descriptor.** Used by `fd`, `c2st` and the
[embedding plots](visualization.md#embedding-projections): the same seven plus
skewness, kurtosis, spectral centroid and spectral bandwidth.
Both descriptors live in
[`_signal_features.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/_signal_features.py).

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
and clipped to \([0, \ln 2]\). `psd` uses the same divergence, applied to the mean spectra,
and `js_div` applies it to pooled amplitude histograms. The functions are in
[`_divergence.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/_divergence.py).

### Matching protocol (`pairing`) { #matching-protocol }

`mse`, `rmse`, `euclidean`, `pearson`, `cosine` and `curve_frechet` score *pairs* of one real and one synthetic signal,
per lead. How the pairs are formed is an explicit choice, because published numbers for the
same metric differ by protocol and are not comparable across protocols:

| `pairing` | Pairs | Valid for |
|---|---|---|
| `"nn"` (default) | Each real signal and its nearest synthetic signal of the same lead. "Nearest" means smallest Euclidean distance for `mse`, `rmse`, `euclidean`, `curve_frechet`, and highest similarity for `pearson`, `cosine`. | Any generator. The only choice for unpaired generation. |
| `"paired"` | Real signal *i* and synthetic signal *i*. Needs the same number of recordings in both sets. | Reconstruction, lead synthesis, signal-to-signal translation. |
| `"mean"` | The mean real waveform and the mean synthetic waveform (one pair per lead). | Beat-aligned inputs only. |

On the command line the protocol is set once for all of these metrics with
`ecgen-eval eval --pairing nn|paired|mean`. The helper is
[`_matching.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/_matching.py).

**Real-vs-real baseline.** The six pairwise metrics also compute the same statistic between
two disjoint random halves of the real set (`baseline=True`, the default) and store it in
`extra["real_vs_real"]` and `extra["per_lead_real_vs_real"]`. It shows what real data scores
against real data under the same protocol, which is the reference a model score has to be
read against. With `pairing="paired"` the two halves are aligned arbitrarily, so the baseline
is then the score of *unrelated* real recordings (chance level), not an upper bound.

**Shared `extra` of the pairwise metrics.** `pairing`, `per_lead_std`, `per_lead_median`,
`per_lead_all_values` (one value per pair; drawn as a violin plot in the report),
`per_lead_n_pairs`, `n_skipped` (pairs without a defined value), `real_vs_real`,
`per_lead_real_vs_real`.

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

### `js_div` — Amplitude JS / KL divergence { #js_div }

:material-school: [Explained](../metrics/js_div.md) ·
:material-api: [`AmplitudeJSMetric`](../api/metrics.md#ecgen_eval.metrics.js_div.AmplitudeJSMetric) ·
:material-github: [`js_div.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/js_div.py)

Per lead, all amplitude values of the real set and of the synthetic set are pooled into two
histograms \(P\) and \(Q\). The bins come from the real data: `n_bins` equal bins between
its 0.1st and 99.9th percentile, plus one open-ended bin on each side, so synthetic values
outside the real range are counted.

\[
\mathrm{JS}(P\|Q) = \tfrac{1}{2}\mathrm{KL}(P\|M) + \tfrac{1}{2}\mathrm{KL}(Q\|M),
\quad M = \tfrac{1}{2}(P+Q)
\]

Range \([0, \ln 2]\). The temporal order of the samples plays no role.

| Parameter | Default | Description |
|---|---|---|
| `n_bins` | `100` | Bins between the 0.1st and 99.9th real percentile |
| `n_subsample` | `1000` | Max recordings per set |
| `eps` | `1e-10` | Smoothing for the KL values in `extra` |
| `seed` | `42` | RNG seed |

`extra`: `kl_real_synth`, `kl_synth_real` and their `per_lead_` versions
(\(\mathrm{KL}(P\|Q)\), \(\mathrm{KL}(Q\|P)\)), `per_lead_js_distance`
(\(\sqrt{\mathrm{JS}}\)), `per_lead_tail_mass` (synthetic probability outside the real
range), `per_lead_hist_real`, `per_lead_hist_synth`, `bin_edges` (used for the histogram
overlay in the report), `n_bins`.

**Reference:** Lin (1991). Divergence measures based on the Shannon entropy. *IEEE Trans.
Information Theory* 37(1), 145–151.
[doi:10.1109/18.61115](https://doi.org/10.1109/18.61115)

### `ks_test` — Kolmogorov–Smirnov test { #ks_test }

:material-school: [Explained](../metrics/ks_test.md) ·
:material-api: [`KSTestMetric`](../api/metrics.md#ecgen_eval.metrics.ks_test.KSTestMetric) ·
:material-github: [`ks_test.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/ks_test.py)

Per lead and for each of the 7 signal features, the two-sample KS statistic between the real
and synthetic feature values:

\[
D = \sup_x \big| F_r(x) - F_s(x) \big|
\]

The lead score is the mean \(D\) over the features. Range \([0, 1]\). The score is an
effect size; p-values are reported in `extra` only, because they depend on the sample size.
They come from `scipy.stats.ks_2samp` when SciPy is installed, otherwise from the asymptotic
Kolmogorov distribution.

| Parameter | Default | Description |
|---|---|---|
| `n_subsample` | `1000` | Max recordings per set |
| `alpha` | `0.05` | Significance level for `n_rejected` |
| `correction` | `"holm"` | Multiple-testing adjustment over features × leads: `"holm"`, `"bonferroni"`, `"none"` |
| `seed` | `42` | RNG seed |

`extra`: `feature_names`, `per_feature_D` (mean over leads), `per_lead_feature_D`,
`per_lead_feature_p`, `per_lead_feature_p_adjusted`, `per_lead_feature_mwu_p` (Mann–Whitney U,
only with SciPy), `n_tests`, `n_rejected`, `frac_rejected`, `alpha`, `correction`, `p_method`
(`"scipy"` or `"asymptotic"`).

The same test on clinical features is available as
[`compare_feature_distributions`](features.md#statistical-comparison).

**Reference:** Massey (1951). The Kolmogorov-Smirnov test for goodness of fit. *J. Am. Stat.
Assoc.* 46(253), 68–78.
[doi:10.1080/01621459.1951.10500769](https://doi.org/10.1080/01621459.1951.10500769)

### `c2st` — Classifier two-sample test { #c2st }

:material-school: [Explained](../metrics/c2st.md) ·
:material-api: [`C2STMetric`](../api/metrics.md#ecgen_eval.metrics.c2st.C2STMetric) ·
:material-github: [`c2st.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/c2st.py)

A classifier is trained to separate real (label 0) from synthetic (label 1) recordings. Both
sets are subsampled to the same size, and predictions are made out-of-fold with stratified
k-fold cross-validation (scaling and PCA are fitted inside each training fold).

\[
\texttt{c2st} = \max\big(0,\ \mathrm{accuracy} - 0.5\big)
\]

Range \([0, 0.5]\); 0 means the classifier is at chance. One classifier is trained per lead;
the score is the mean over leads. A classifier on all leads together is reported in `extra`.

| Parameter | Default | Description |
|---|---|---|
| `classifier` | `"logreg"` | `"logreg"` (logistic regression), `"rf"` (random forest, 100 trees) or `"knn"` (1-NN) |
| `features` | `"handcrafted"` | `"handcrafted"` (11-feature descriptor) or `"signal"` (waveform decimated to ≤ 250 points, PCA to ≤ 32 components) |
| `n_splits` | `5` | Cross-validation folds (reduced automatically for small sets) |
| `n_subsample` | `1000` | Max recordings per class |
| `seed` | `42` | RNG seed |

`extra`: `accuracy`, `auc` (means over leads), `per_lead_accuracy`, `per_lead_auc`,
`per_lead_fold_accuracy`, `all_leads` (`accuracy`, `auc`, `score`, `p_above_chance`),
`feature_importance` (mean absolute logistic-regression coefficient per feature; default
settings only), `one_nn_loo_accuracy` (leave-one-out 1-NN accuracy on all-lead features, up to
2000 recordings), `classifier`, `features`, `n_per_class`, `n_splits`.

With fewer than 4 recordings per class the score is NaN and a warning is raised.

**Reference:** Lopez-Paz & Oquab (2017). Revisiting classifier two-sample tests. *ICLR*.
[arXiv:1610.06545](https://arxiv.org/abs/1610.06545). Discriminative score: Yoon, Jarrett &
van der Schaar (2019). Time-series generative adversarial networks. *NeurIPS* 32.

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

`mse`, `rmse`, `euclidean`, `pearson`, `cosine` and `curve_frechet` let you choose: nearest
neighbour per lead by default, or index-aligned pairs, or mean waveforms. See
[Matching protocol](#matching-protocol).

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

### `mse` — Mean Squared Error { #mse }

:material-school: [Explained](../metrics/mse.md) ·
:material-api: [`MSEMetric`](../api/metrics.md#ecgen_eval.metrics.mse.MSEMetric) ·
:material-github: [`mse.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/mse.py)

\[
\mathrm{MSE} = \frac{1}{T}\sum_{t=1}^{T} \big(x_r[t] - x_s[t]\big)^2
\]

Mean over the matched pairs of each lead.

| Parameter | Default | Description |
|---|---|---|
| `pairing` | `"nn"` | `"nn"`, `"paired"` or `"mean"`; see [Matching protocol](#matching-protocol) |
| `n_subsample` | `500` | Max recordings per set |
| `normalize` | `None` | Per recording and lead, before matching: `None`, `"zscore"` or `"minmax"` |
| `baseline` | `True` | Also score two halves of the real set |
| `seed` | `42` | RNG seed |

`extra`: `rmse`, `per_lead_rmse`, `normalize`, and the
[shared pairwise extras](#matching-protocol).

**Reference:** Wang & Bovik (2009). Mean squared error: Love it or leave it? A new look at
signal fidelity measures. *IEEE Signal Processing Magazine* 26(1), 98–117.
[doi:10.1109/MSP.2008.930649](https://doi.org/10.1109/MSP.2008.930649)

### `rmse` — Root Mean Square Error { #rmse }

:material-school: [Explained](../metrics/mse.md) ·
:material-api: [`RMSEMetric`](../api/metrics.md#ecgen_eval.metrics.mse.RMSEMetric) ·
:material-github: [`mse.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/mse.py)

\[
\mathrm{RMSE} = \sqrt{\frac{1}{T}\sum_{t=1}^{T} \big(x_r[t] - x_s[t]\big)^2}
\]

The mean of the per-pair RMSE (not the root of the mean MSE). With default settings it equals
`extra["rmse"]` of [`mae`](#mae). Same parameters as [`mse`](#mse).

`extra`: `mse`, `per_lead_mse`, `nrmse`, `per_lead_nrmse` (RMSE divided by the peak-to-peak
range of the real signal), `normalize`, and the
[shared pairwise extras](#matching-protocol).

**Reference:** as for [`mse`](#mse).

### `euclidean` — Euclidean distance { #euclidean }

:material-school: [Explained](../metrics/euclidean.md) ·
:material-api: [`EuclideanMetric`](../api/metrics.md#ecgen_eval.metrics.euclidean.EuclideanMetric) ·
:material-github: [`euclidean.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/euclidean.py)

\[
\mathrm{ED} = \sqrt{\sum_{t=1}^{T} \big(x_r[t]-x_s[t]\big)^2} = \sqrt{T}\cdot\mathrm{RMSE}
\]

Grows with the number of samples \(T\); compare only recordings of equal length. Same
parameters as [`mse`](#mse).

`extra`: `length_normalised` (\(\mathrm{ED}/\sqrt{T}\), equal to `rmse`), `n_timepoints`,
their `per_lead_` versions, `normalize`, and the
[shared pairwise extras](#matching-protocol).

**Reference:** Wang et al. (2013). Experimental comparison of representation methods and
distance measures for time series data. *Data Mining and Knowledge Discovery* 26, 275–309.
[doi:10.1007/s10618-012-0250-5](https://doi.org/10.1007/s10618-012-0250-5)

### `pearson` — Pearson correlation { #pearson }

:material-school: [Explained](../metrics/pearson.md) ·
:material-api: [`PearsonMetric`](../api/metrics.md#ecgen_eval.metrics.pearson.PearsonMetric) ·
:material-github: [`pearson.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/pearson.py)

\[
r = \frac{\sum_t (x_r[t]-\bar x_r)(x_s[t]-\bar x_s)}
{\sqrt{\sum_t (x_r[t]-\bar x_r)^2}\,\sqrt{\sum_t (x_s[t]-\bar x_s)^2}}
\]

Range \([-1, 1]\), **higher is better**. With `pairing="nn"` the neighbour is the
best-correlated synthetic signal. Pairs with a zero-variance signal are skipped.

| Parameter | Default | Description |
|---|---|---|
| `pairing` | `"nn"` | `"nn"`, `"paired"` or `"mean"`; see [Matching protocol](#matching-protocol) |
| `n_subsample` | `500` | Max recordings per set |
| `max_lag_ms` | `0.0` | If > 0, also report the largest cross-correlation within ± this lag |
| `fs` | `500.0` | Sampling rate (Hz), used for `max_lag_ms` only |
| `baseline` | `True` | Also score two halves of the real set |
| `seed` | `42` | RNG seed |

`extra`: with `max_lag_ms > 0`, `xcorr_max` and `best_lag_ms` (positive: the synthetic signal
is late) and their `per_lead_` versions; plus the
[shared pairwise extras](#matching-protocol).

**Reference:** Pearson (1895). Note on regression and inheritance in the case of two parents.
*Proc. R. Soc. London* 58, 240–242.
[doi:10.1098/rspl.1895.0041](https://doi.org/10.1098/rspl.1895.0041)

### `cosine` — Cosine similarity { #cosine }

:material-school: [Explained](../metrics/cosine.md) ·
:material-api: [`CosineMetric`](../api/metrics.md#ecgen_eval.metrics.cosine.CosineMetric) ·
:material-github: [`cosine.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/cosine.py)

\[
\cos(x_r, x_s) = \frac{\sum_t x_r[t]\,x_s[t]}{\lVert x_r\rVert\,\lVert x_s\rVert}
\]

Range \([-1, 1]\), **higher is better**. Pearson correlation without mean removal. With
`pairing="nn"` the neighbour is the most similar synthetic signal. All-zero signals are
skipped.

| Parameter | Default | Description |
|---|---|---|
| `pairing` | `"nn"` | `"nn"`, `"paired"` or `"mean"`; see [Matching protocol](#matching-protocol) |
| `n_subsample` | `500` | Max recordings per set |
| `baseline` | `True` | Also score two halves of the real set |
| `seed` | `42` | RNG seed |

`extra`: the [shared pairwise extras](#matching-protocol).

**Reference:** Singhal (2001). Modern information retrieval: A brief overview. *IEEE Data
Engineering Bulletin* 24(4), 35–43.

### `curve_frechet` — Discrete (curve) Fréchet distance { #curve_frechet }

:material-school: [Explained](../metrics/curve_frechet.md) ·
:material-api: [`CurveFrechetMetric`](../api/metrics.md#ecgen_eval.metrics.curve_frechet.CurveFrechetMetric) ·
:material-github: [`curve_frechet.py`](https://github.com/vlbthambawita/ECGEN-Eval/blob/main/ecgen_eval/metrics/curve_frechet.py)

Not related to the Gaussian Fréchet distance of [`fd`](#fd) and [`fed`](#fed). For curves
\(P=(p_1..p_n)\) and \(Q=(q_1..q_m)\):

\[
c(i,j) = \max\Big(\min\big(c(i-1,j),\, c(i-1,j-1),\, c(i,j-1)\big),\ d(p_i,q_j)\Big),
\qquad \mathrm{DFD} = c(n,m)
\]

with \(d(p_i,q_j) = \sqrt{(x_r[i]-x_s[j])^2 + (w\,(t_i-t_j))^2}\) and
\(w\) = `time_weight`. Signals are decimated to at most `max_len` points before matching.

| Parameter | Default | Description |
|---|---|---|
| `pairing` | `"nn"` | `"nn"`, `"paired"` or `"mean"`; see [Matching protocol](#matching-protocol) |
| `n_pairs` | `100` | Max real signals scored per lead |
| `max_len` | `500` | Max points per curve after decimation |
| `time_weight` | `0.0` | Weight of the time axis (signal units per second); 0 compares amplitudes only |
| `fs` | `500.0` | Sampling rate (Hz), used when `time_weight > 0` |
| `n_candidates` | `500` | Max synthetic signals searched for the nearest neighbour |
| `baseline` | `True` | Also score two halves of the real set |
| `seed` | `42` | RNG seed |

`extra`: `n_points`, `effective_fs`, `time_weight`, their `per_lead_` versions, and the
[shared pairwise extras](#matching-protocol).

**Reference:** Eiter & Mannila (1994). Computing discrete Fréchet distance. Technical Report
CD-TR 94/64, TU Vienna. Applied to synthetic ECG in Delaney, Brophy & Ward (2019).
[arXiv:1909.09150](https://arxiv.org/abs/1909.09150)

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
