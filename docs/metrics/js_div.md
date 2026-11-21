# Amplitude JS / KL Divergence

**Key:** `js_div` · **Family:** distribution · **Better:** lower ↓ · **Per-lead:** yes

This metric asks: *do real and synthetic ECGs use the same amplitude values, equally often?*
It pools every sample of every recording into one histogram per set and compares the two
histograms with the Jensen–Shannon (JS) divergence. 18 papers in the
[literature review](../literature/database.md#metrics/Fidelity) report a KL or JS divergence, most of them on
amplitude distributions.

## Try it

The upper plot shows part of the synthetic strip. The lower plot shows both amplitude
histograms; the outermost bars collect synthetic values outside the real range.

<div class="mviz" data-viz="amplitudeJS">Interactive demo loading… (needs JavaScript)</div>

What to notice:

- **Gain 1.5×** and **Baseline offset**: the histograms shift apart and JS rises. Pearson
  correlation would not see either change.
- **Too clean**: without noise the baseline samples pile up in one bin. A generator that
  removes the noise floor is detected.
- **Clipped R peaks**: the large amplitudes vanish from the synthetic histogram.
- **Shuffled in time**: the score does not change at all. The metric ignores the order of the
  samples, so it cannot tell an ECG from the same values in random order.

## How it works

1. Per lead, pool the amplitude values of up to `n_subsample` real recordings, and of the
   synthetic recordings.
2. Build the bins from the **real** data: `n_bins` (default 100) equal bins between the 0.1st
   and 99.9th real percentile, plus one open-ended bin on each side. Synthetic values outside
   the real range land in those two tail bins instead of being dropped.
3. Normalise both histograms to probabilities \(P\) (real) and \(Q\) (synthetic).
4. Compute JS; the score is the mean over leads.

## The math

\[
\mathrm{JS}(P \,\|\, Q) = \tfrac12\,\mathrm{KL}(P \,\|\, M) + \tfrac12\,\mathrm{KL}(Q \,\|\, M),
\qquad M = \tfrac12 (P + Q),
\qquad \mathrm{KL}(P \,\|\, Q) = \sum_i P_i \ln \frac{P_i}{Q_i}
\]

JS is the score because it is symmetric, bounded by \(\ln 2 \approx 0.693\), and finite
when a bin is empty. Papers often quote KL, so both directions are in `extra`
(`kl_real_synth`, `kl_synth_real`), computed with a small smoothing constant `eps`.

## Reading the score

- 0 = identical amplitude distributions; \(\ln 2\) = no overlap.
- `extra["per_lead_tail_mass"]` is the share of synthetic samples outside the real amplitude
  range. A high value points to gain errors or outliers.
- KL is not symmetric and depends strongly on binning and smoothing. Compare KL values only
  between runs with the same `n_bins` and `eps`; published values (0.01 to 3.4 in
  [P171](../literature/database.md#papers/P171)) are not comparable with each other.
- The metric sees gain, offset, clipping and noise-floor differences. It is blind to
  morphology and rhythm. Pair it with a shape metric ([`pearson`](pearson.md),
  [`dtw`](dtw.md)) and a rhythm metric ([`heart_rate`](heart_rate.md)).
- The HTML report shows the two histograms per lead next to the score.

Other ECGEN-Eval metrics use the same divergence on different quantities:
[`psd`](psd.md) on power spectra, [`spectral_entropy`](spectral_entropy.md),
[`heart_rate`](heart_rate.md) and [`hrv`](hrv.md) on one value per recording.

## Use it with ECGEN-Eval

=== "CLI"

    ```bash
    ecgen-eval eval --real real.npy --synthetic synth.npy -m js_div --output report.html
    ```

=== "Python"

    ```python
    from ecgen_eval import load_ecg_npy, AVAILABLE_METRICS

    real = load_ecg_npy("real.npy", fs=500)
    synth = load_ecg_npy("synth.npy", fs=500)

    result = AVAILABLE_METRICS["js_div"]().compute(real.data, synth.data, lead_names=real.lead_names)
    print("JS:", result.score, "KL(real‖synth):", result.extra["kl_real_synth"])
    ```

Parameters are in the [Metric Reference](../user-guide/metric-reference.md#js_div).

## Learn more

- Lin (1991). Divergence measures based on the Shannon entropy. *IEEE Trans. Information
  Theory* 37(1), 145–151. [doi:10.1109/18.61115](https://doi.org/10.1109/18.61115)
- Kullback & Leibler (1951). On information and sufficiency. *Ann. Math. Statist.* 22(1),
  79–86. [doi:10.1214/aoms/1177729694](https://doi.org/10.1214/aoms/1177729694)
- How papers use it: [Paper Database](../literature/database.md#metrics/Fidelity), family *KL / JS divergence*.
