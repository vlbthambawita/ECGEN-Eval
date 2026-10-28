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
| Does the synthetic **population** match the real one? | [FED](fed.md), [FD](fd.md), [MMD](mmd.md), [SWD](swd.md) |
| Are samples **realistic**, and is the real **diversity covered**? | [Precision & Recall](pr_dist.md) |
| Does each real ECG have a close synthetic **look-alike**? | [PRD](prd.md), [MAE](mae.md), [PSNR](psnr.md), [SSIM](ssim.md), [DTW](dtw.md) |
| Do beats have the right **shape**? | [SQI](sqi.md) |
| Is the **frequency content** right? | [PSD](psd.md), [Spectral entropy](spectral_entropy.md) |
| Is the **rhythm** physiological? | [Heart rate](heart_rate.md), [HRV](hrv.md) |
| Is the model **copying** its training data? | [Nearest-neighbour distance](nn_dist.md) |

Always compare against a **real-vs-real baseline**: score two disjoint halves of your real data
with the same metric. That shows what "as good as real data" looks like for your data set.
The [Metric Reference](../user-guide/metric-reference.md) lists every parameter, and the
[Paper Database](../literature/database.md#metrics/Fidelity) shows how the literature uses
each metric family.
