# Metrics Explained

Each page below explains one ECGEN-Eval metric with an **interactive visualization**: move the
sliders or click a preset to change the synthetic data and watch the score respond. Every page
also covers how the metric is computed, the maths, how to read the score, and how to run it
with ECGEN-Eval.

!!! tip "How the demos work"
    The demos run in your browser on small simulated data sets (a few hundred points or a
    handful of simulated ECG beats). They use the same formulas as ECGEN-Eval, so the scores
    behave the same way. The absolute numbers will differ from scores on your own recordings.

<div class="grid cards" markdown>

-   :material-chart-bell-curve: **[Fréchet ECG Distance (FED)](fed.md)** · `fed` · ↓

    ---

    Compares Gaussians fitted to embeddings from a pre-trained ECG foundation model, like
    FID for images.

-   :material-chart-bell-curve-cumulative: **[Fréchet Distance (FD)](fd.md)** · `fd` · ↓

    ---

    The same Fréchet distance on 11 handcrafted signal features per lead. No GPU needed.

-   :material-vector-difference: **[Maximum Mean Discrepancy](mmd.md)** · `mmd` · ↓

    ---

    A kernel two-sample test that detects any difference in distribution shape, not just in
    mean and variance.

-   :material-angle-acute: **[Sliced Wasserstein Distance](swd.md)** · `swd` · ↓

    ---

    Projects the data onto many random lines and averages the 1-D transport distances.

-   :material-target: **[Precision & Recall](pr_dist.md)** · `pr_dist` · ↑

    ---

    Splits quality into *realism* (precision) and *coverage* (recall) using k-NN manifolds.

-   :material-chart-histogram: **[Amplitude JS / KL Divergence](js_div.md)** · `js_div` · ↓

    ---

    Compares which amplitude values the two sets use and how often. Sees gain, offset and
    clipping errors.

-   :material-chart-line-stacked: **[Kolmogorov–Smirnov Test](ks_test.md)** · `ks_test` · ↓

    ---

    The largest gap between two cumulative distributions, per signal feature, with p-values.

-   :material-robot-confused-outline: **[Classifier Two-Sample Test](c2st.md)** · `c2st` · ↓

    ---

    Trains a classifier to tell real from synthetic. Chance-level accuracy means
    indistinguishable.

-   :material-sine-wave: **[Dynamic Time Warping](dtw.md)** · `dtw` · ↓

    ---

    A waveform distance that tolerates small timing differences by aligning the signals first.

-   :material-percent: **[Percent RMS Difference](prd.md)** · `prd` · ↓

    ---

    Point-wise error relative to the energy of the real signal, the classic ECG compression metric.

-   :material-ruler: **[Mean Absolute Error](mae.md)** · `mae` · ↓

    ---

    Average absolute amplitude difference to the nearest synthetic signal (RMSE alongside).

-   :material-signal: **[Peak Signal-to-Noise Ratio](psnr.md)** · `psnr` · ↑

    ---

    Point-wise error expressed in decibels relative to the signal's peak-to-peak range.

-   :material-shape-outline: **[Structural Similarity](ssim.md)** · `ssim` · ↑

    ---

    Compares mean, variance and correlation (shape) instead of raw sample differences.

-   :material-square-root: **[MSE and RMSE](mse.md)** · `mse`, `rmse` · ↓

    ---

    Squared point-wise error and its square root, the most reported fidelity numbers in the
    literature.

-   :material-ruler-square: **[Euclidean Distance](euclidean.md)** · `euclidean` · ↓

    ---

    Straight-line distance between two waveforms; RMSE scaled by the signal length.

-   :material-chart-timeline-variant: **[Pearson Correlation](pearson.md)** · `pearson` · ↑

    ---

    Do the two waveforms rise and fall together? Ignores amplitude scale and offset.

-   :material-angle-right: **[Cosine Similarity](cosine.md)** · `cosine` · ↑

    ---

    The angle between two signals seen as vectors. Pearson without mean removal.

-   :material-vector-polyline: **[Curve Fréchet Distance](curve_frechet.md)** · `curve_frechet` · ↓

    ---

    The largest gap that remains after the best time alignment of two curves. Not the
    Fréchet distance of FD and FED.

-   :material-heart-pulse: **[Signal Quality Index](sqi.md)** · `sqi` · ↑

    ---

    Correlation of each synthetic ECG with a morphology template built from the real data.

-   :material-chart-histogram: **[PSD divergence](psd.md)** · `psd` · ↓

    ---

    Compares the average frequency content (power spectra) of the two sets.

-   :material-chart-scatter-plot: **[Spectral Entropy](spectral_entropy.md)** · `spectral_entropy` · ↓

    ---

    Compares how concentrated or spread out each recording's spectrum is.

-   :material-heart-cog: **[Heart Rate](heart_rate.md)** · `heart_rate` · ↓

    ---

    Detects R peaks and compares the heart-rate distributions.

-   :material-timeline-clock-outline: **[Heart-Rate Variability](hrv.md)** · `hrv` · ↓

    ---

    Compares SDNN, RMSSD and pNN50: how much and how irregularly the beat timing varies.

-   :material-shield-lock-outline: **[Nearest-Neighbour Distance](nn_dist.md)** · `nn_dist` · ↓

    ---

    Checks for memorisation: are synthetic ECGs near-copies of real training recordings?

</div>

↓ lower is better · ↑ higher is better.

## Which metrics should I use?

No single metric captures everything. A balanced evaluation covers several of these questions:

| Question | Metrics |
|---|---|
| Does the synthetic **population** match the real one? | [FED](fed.md), [FD](fd.md), [MMD](mmd.md), [SWD](swd.md), [KS test](ks_test.md) |
| Can a classifier **tell them apart**? | [Classifier two-sample test](c2st.md) |
| Are **amplitudes** (gain, offset, noise floor) right? | [Amplitude JS / KL](js_div.md) |
| Are samples **realistic**, and is the real **diversity covered**? | [Precision & Recall](pr_dist.md) |
| Does each real ECG have a close synthetic **look-alike**? | [PRD](prd.md), [MAE](mae.md), [MSE / RMSE](mse.md), [Euclidean](euclidean.md), [PSNR](psnr.md), [SSIM](ssim.md), [DTW](dtw.md), [Curve Fréchet](curve_frechet.md) |
| Do beats have the right **shape**? | [SQI](sqi.md), [Pearson](pearson.md), [Cosine](cosine.md) |
| Is the **frequency content** right? | [PSD](psd.md), [Spectral entropy](spectral_entropy.md) |
| Is the **rhythm** physiological? | [Heart rate](heart_rate.md), [HRV](hrv.md) |
| Is the model **copying** its training data? | [Nearest-neighbour distance](nn_dist.md) |

Always compare against a **real-vs-real baseline**: score two disjoint halves of your real data
with the same metric. That shows what "as good as real data" looks like for your data set.
The pairwise metrics (`mse`, `rmse`, `euclidean`, `pearson`, `cosine`, `curve_frechet`) compute
this baseline for you and report it as `extra["real_vs_real"]`.

## Which metric did the paper use?

The [Paper Database](../literature/database.md#metrics/Fidelity) groups what papers report
into metric families. Every Fidelity family used by more than 10 of the reviewed papers has
an ECGEN-Eval counterpart:

| Family in the literature review | Papers | ECGEN-Eval |
|---|:-:|---|
| Visual inspection (qualitative) | 62 | [ECG gallery and beat-morphology bands](../user-guide/visualization.md#beat-morphology) |
| RMSE | 55 | [`rmse`](mse.md) |
| DTW | 44 | [`dtw`](dtw.md) |
| Pearson / correlation | 41 | [`pearson`](pearson.md) |
| FID / embedding Fréchet | 39 | [`fed`](fed.md), [`fd`](fd.md) |
| MSE | 30 | [`mse`](mse.md) |
| MAE | 29 | [`mae`](mae.md) |
| t-SNE / UMAP / PCA plots | 26 | [Embedding projections](../user-guide/visualization.md#embedding-projections) |
| MMD | 26 | [`mmd`](mmd.md) |
| Curve Fréchet distance | 24 | [`curve_frechet`](curve_frechet.md) |
| PSNR / SNR | 23 | [`psnr`](psnr.md) |
| PRD / normalised PRD | 21 | [`prd`](prd.md) |
| Statistical tests | 19 | [`ks_test`](ks_test.md) |
| KL / JS divergence | 18 | [`js_div`](js_div.md) |
| Spectral / PSD similarity | 16 | [`psd`](psd.md), [`spectral_entropy`](spectral_entropy.md) |
| Wasserstein / EMD | 14 | [`swd`](swd.md) |
| Classifier two-sample test | 14 | [`c2st`](c2st.md) |
| SSIM | 13 | [`ssim`](ssim.md) |
| Euclidean distance | 12 | [`euclidean`](euclidean.md) |
| Cosine similarity | 12 | [`cosine`](cosine.md) |

Before comparing your number with a published one, check the pairing (nearest neighbour,
paired or class mean), the amplitude units and normalisation, and the signal length. See
[Matching protocol](../user-guide/metric-reference.md#matching-protocol).

The [Metric Reference](../user-guide/metric-reference.md) lists every parameter, and the
[Paper Database](../literature/database.md#metrics/Fidelity) shows how the literature uses
each metric family.
