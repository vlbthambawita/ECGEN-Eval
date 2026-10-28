# Signal Quality Index (SQI)

**Key:** `sqi` · **Family:** morphology · **Better:** higher ↑ · **Per-lead:** yes

SQI asks: *do the synthetic ECGs have the typical shape of the real ECGs?* It builds a
template, the average real recording, and measures how well each synthetic recording
correlates with it.

## Try it

The bold line is the template from 25 real beats. Thin lines are synthetic beats. Every beat
is first scaled to the range 0–1, so only *shape* matters, not amplitude.

<div class="mviz" data-viz="sqi">Interactive demo loading… (needs JavaScript)</div>

What to notice:

- **Wide QRS** and **inverted T** lower SQI because the shape differs from the template.
- **Misaligned beats**: SQI also drops when beats are not at the same position, because
  correlation is computed sample by sample. On whole recordings with different heart rates
  the real template itself becomes blurred.
- The **real self-SQI** is the ceiling: real beats are not perfectly correlated with their
  own average either.

## How it works

For each lead:

1. Scale every real recording to unit range and average them: this is the **template**.
2. Scale every synthetic recording to unit range.
3. Compute the **Pearson correlation** of each synthetic recording with the template.
4. Average. `extra["real_self_sqi"]` gives the same average for the real recordings.

## The math

\[
\tilde x = \frac{x - \min x}{\max x - \min x},
\qquad
\mathcal T = \frac{1}{n}\sum_{i=1}^{n} \tilde x_i^{\,r},
\qquad
\mathrm{SQI} = \frac{1}{m}\sum_{j=1}^{m} \rho\!\left(\tilde x_j^{\,s},\ \mathcal T\right)
\]

with \(\rho\) the Pearson correlation.

## Reading the score

- Range **[−1, 1]**; compare with `real_self_sqi`. A synthetic SQI close to the real
  self-SQI means typical morphology.
- SQI rewards resemblance to the **average** ECG. A generator that outputs the mean beat
  every time scores very well while having no diversity, so pair SQI with
  [Precision & Recall](pr_dist.md) or a distribution metric.
- Works best on aligned, single-beat or fixed-rhythm data. For multi-beat recordings with
  varying heart rates the template is blurred, and SQI mostly reflects rhythm alignment.

## Use it with ECGEN-Eval

=== "CLI"

    ```bash
    ecgen-eval eval --real real.npy --synthetic synth.npy -m sqi --output report.html
    ```

=== "Python"

    ```python
    from ecgen_eval import load_ecg_npy, AVAILABLE_METRICS

    real = load_ecg_npy("real.npy", fs=500)
    synth = load_ecg_npy("synth.npy", fs=500)

    result = AVAILABLE_METRICS["sqi"]().compute(real.data, synth.data, lead_names=real.lead_names)
    print("SQI:", result.score, "real self-SQI:", result.extra["real_self_sqi"])
    ```

Parameters are in the [Metric Reference](../user-guide/metric-reference.md#sqi).
