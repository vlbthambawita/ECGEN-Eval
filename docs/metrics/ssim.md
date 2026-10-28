# Structural Similarity (SSIM)

**Key:** `ssim` · **Family:** signal fidelity · **Better:** higher ↑ · **Per-lead:** yes

SSIM asks: *do two signals have the same level, the same variation and the same shape?*
Instead of summing raw differences it compares three statistics, which makes it closer to
how a person judges similarity. ECGEN-Eval uses a global (whole-signal) 1-D version.

## Try it

The two extra cards split SSIM into a **luminance** term (are the means equal?) and a
**contrast × structure** term (are the variations equal and correlated?).

<div class="mviz" data-viz="pointwise" data-highlight="ssim">Interactive demo loading… (needs JavaScript)</div>

What to notice:

- **Amplitude** changes lower only the contrast part, and only a little: a beat at 80 %
  amplitude still has SSIM near 1, while PRD calls it a 20 % error.
- **Baseline drift** affects the luminance term.
- **Inverted T wave** and **20 ms late** reduce the correlation (structure), which is the
  part that matters most.

## How it works

1. For each real recording, find the **nearest synthetic recording**.
2. Per lead, compute the means, variances and covariance over the whole signal, and the
   stabilising constants from the real signal's dynamic range \(L\).
3. Combine them into SSIM and average; the score is the mean over leads.

## The math

\[
\mathrm{SSIM}(x,y) =
\underbrace{\frac{2\mu_x\mu_y + C_1}{\mu_x^2 + \mu_y^2 + C_1}}_{\text{luminance}}\cdot
\underbrace{\frac{2\sigma_{xy} + C_2}{\sigma_x^2 + \sigma_y^2 + C_2}}_{\text{contrast}\times\text{structure}}
\]

with \(C_1 = (0.01L)^2\), \(C_2 = (0.03L)^2\) and \(L\) the range of the real signal. The
second factor equals \(c\cdot s\) when \(C_3 = C_2/2\), with \(c\) the contrast and \(s\)
the Pearson correlation.

## Reading the score

- Range **[−1, 1]**; 1 means identical. Negative values mean anti-correlated signals.
- This is the **global** form: one value per signal, not a sliding-window average as in
  image SSIM, so local errors are averaged out.
- SSIM is insensitive to modest amplitude scaling, which is useful when gain differs but
  can hide clinically relevant voltage changes (for example low-voltage ECGs).

## Use it with ECGEN-Eval

=== "CLI"

    ```bash
    ecgen-eval eval --real real.npy --synthetic synth.npy -m ssim --output report.html
    ```

=== "Python"

    ```python
    from ecgen_eval import load_ecg_npy, AVAILABLE_METRICS

    real = load_ecg_npy("real.npy", fs=500)
    synth = load_ecg_npy("synth.npy", fs=500)

    result = AVAILABLE_METRICS["ssim"](k1=0.01, k2=0.03).compute(real.data, synth.data, lead_names=real.lead_names)
    print(result.score, result.per_lead_scores)
    ```

Parameters are in the [Metric Reference](../user-guide/metric-reference.md#ssim).

## Learn more

- Wang et al., *Image Quality Assessment: From Error Visibility to Structural Similarity*,
  IEEE TIP 2004.
- Hayn et al., applied to ECG in *Physiological Measurement* 2018.
