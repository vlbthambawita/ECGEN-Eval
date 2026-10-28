# Percent Root-mean-square Difference (PRD)

**Key:** `prd` · **Family:** signal fidelity · **Better:** lower ↓ · **Per-lead:** yes

PRD asks: *how large is the point-by-point error compared with the size of the real signal?*
It comes from ECG compression, where it measures how much a compressed signal deviates from
the original.

## Try it

The shaded area is the point-wise error between a real beat and its synthetic nearest
neighbour. All five point-wise metrics are shown; PRD is highlighted.

<div class="mviz" data-viz="pointwise" data-highlight="prd">Interactive demo loading… (needs JavaScript)</div>

What to notice:

- **20 ms late**: a small timing shift of a perfect beat gives a large PRD, because the
  sharp R peak no longer overlaps. Point-wise metrics punish phase shifts hard; see
  [DTW](dtw.md) for a shift-tolerant alternative.
- **Baseline drift** adds error everywhere, even though the beat shape is perfect.
- Amplitude changes scale the error directly.

## How it works

1. For each real recording (up to `n_subsample`), find the **nearest synthetic recording**:
   the one with the smallest Euclidean distance over all leads jointly.
2. For each lead, compute PRD between the real recording and that neighbour.
3. Average over recordings; the score is the mean over leads.

Because generated ECGs are not paired with real ones, the nearest-neighbour match finds the
synthetic ECG that best explains each real ECG.

## The math

\[
\mathrm{PRD} = 100 \cdot \frac{\lVert x_r - x_s \rVert_2}{\lVert x_r \rVert_2}
= 100\cdot\sqrt{\frac{\sum_t (x_r[t]-x_s[t])^2}{\sum_t x_r[t]^2}}
\]

## Reading the score

- **0 %** is a perfect match. In compression work, PRD below about 9 % is often called
  "good" quality. Generated ECGs are rarely that close, so compare against a real-vs-real
  baseline.
- The denominator includes the DC level: a signal with a baseline offset has a larger
  \(\lVert x_r\rVert\), so PRD depends on preprocessing. Some papers use a mean-removed
  variant (PRDN).
- PRD rewards a *close look-alike* for each real ECG. It says nothing about whether the
  synthetic set is diverse or realistic overall; use it with a distribution metric.

## Use it with ECGEN-Eval

=== "CLI"

    ```bash
    ecgen-eval eval --real real.npy --synthetic synth.npy -m prd --output report.html
    ```

=== "Python"

    ```python
    from ecgen_eval import load_ecg_npy, AVAILABLE_METRICS

    real = load_ecg_npy("real.npy", fs=500)
    synth = load_ecg_npy("synth.npy", fs=500)

    result = AVAILABLE_METRICS["prd"](n_subsample=500).compute(real.data, synth.data, lead_names=real.lead_names)
    print(f"PRD = {result.score:.1f} %")
    ```

Parameters are in the [Metric Reference](../user-guide/metric-reference.md#prd).

## Learn more

- Zigel, Cohen & Katz, *The weighted diagnostic distortion (WDD) measure for ECG signal
  compression*, IEEE TBME 2000.
- Related point-wise metrics: [MAE](mae.md), [PSNR](psnr.md), [SSIM](ssim.md).
