# Spectral Entropy divergence

**Key:** `spectral_entropy` · **Family:** spectral · **Better:** lower ↓ · **Per-lead:** yes ·
**Uses:** `fs`

Spectral entropy measures how **spread out** a recording's spectrum is. A clean ECG
concentrates power in a few low frequencies (low entropy); noise spreads it across all
frequencies (high entropy). The metric asks: *do the real and synthetic sets have the same
distribution of spectral entropies?*

## Try it

Each bar counts recordings with a given spectral entropy. The real set includes recordings
with different noise levels, as real data does.

<div class="mviz" data-viz="spectralEntropy">Interactive demo loading… (needs JavaScript)</div>

What to notice:

- **Too clean** or **too noisy** shifts the whole synthetic histogram.
- **All alike**: same average noise, but no variation between recordings. The histogram
  becomes narrow, and the divergence rises even though the [PSD](psd.md) average would look
  fine. This is what this metric adds over `psd`.

## How it works

For each lead:

1. Compute each recording's PSD (Welch with SciPy, FFT otherwise) and normalise it to sum
   to 1.
2. Compute its Shannon entropy in bits.
3. Histogram the real and synthetic entropies with **50 bins** over their joint range.
4. Compute the Jensen–Shannon divergence between the two histograms.

The score is the mean over leads.

## The math

\[
\mathrm{SE}(x) = -\sum_f p(f)\,\log_2 p(f),
\qquad p(f) = \frac{S_x(f)}{\sum_{f'} S_x(f')}
\]

\[
\text{score} = \mathrm{JS}\big(\mathrm{hist}(\mathrm{SE}^{r}),\ \mathrm{hist}(\mathrm{SE}^{s})\big)
\in [0, \ln 2]
\]

## Reading the score

- 0 means identical entropy distributions; ln 2 ≈ 0.693 means no overlap at all.
- With 50 bins and only a few hundred recordings, histograms are sparse and the score is
  noisy. Use as many recordings as possible and compare against a real-vs-real baseline.
- Per-lead means and standard deviations of the entropies are in `extra` and are often easier
  to interpret than the divergence itself.

## Use it with ECGEN-Eval

=== "CLI"

    ```bash
    ecgen-eval eval --real real.npy --synthetic synth.npy -m spectral_entropy --fs 500 --output report.html
    ```

=== "Python"

    ```python
    from ecgen_eval import load_ecg_npy, AVAILABLE_METRICS

    real = load_ecg_npy("real.npy", fs=500)
    synth = load_ecg_npy("synth.npy", fs=500)

    se = AVAILABLE_METRICS["spectral_entropy"](fs=real.fs)
    result = se.compute(real.data, synth.data, lead_names=real.lead_names)
    print(result.score, result.extra)   # extra[lead]: real/synth SE mean and std
    ```

Parameters are in the [Metric Reference](../user-guide/metric-reference.md#spectral_entropy).

## Learn more

- Inouye et al., *Quantification of EEG irregularity by use of the entropy of the power
  spectrum*, Electroencephalogr. Clin. Neurophysiol. 1991.
