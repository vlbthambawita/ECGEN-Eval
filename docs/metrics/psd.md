# Power Spectral Density divergence (PSD)

**Key:** `psd` · **Family:** spectral · **Better:** lower ↓ · **Per-lead:** yes · **Uses:** `fs`

PSD asks: *is the power distributed over the same frequencies in the real and synthetic
ECGs?* Heart rate, QRS sharpness, noise, mains interference and baseline wander all leave
fingerprints in the spectrum that are hard to see in the waveform.

## Try it

Top: the first 4 s of one real (upper) and one synthetic (lower) recording. Bottom: the
average normalised spectrum of each set, on a log scale.

<div class="mviz" data-viz="psd">Interactive demo loading… (needs JavaScript)</div>

What to notice:

- **Mains hum** adds a sharp peak at 50 Hz that is barely visible in the waveform.
- **High-frequency noise** lifts the whole tail above 30 Hz, where real ECGs have little power.
- **Baseline wander** moves power to below 1 Hz.
- **Faster rhythm** shifts the harmonic peaks of the heart rate to the right.

## How it works

For each lead:

1. Compute the PSD of every recording: Welch's method (SciPy, Hann segments of
   `nperseg = min(256, T)` samples) or a plain FFT periodogram without SciPy.
2. Average the PSDs over the real set and over the synthetic set.
3. Normalise each average to sum to 1, so that it is a distribution over frequency.
4. Compute the Jensen–Shannon divergence between the two distributions.

The score is the mean over leads. The mean PSDs are kept in `extra` and drawn in the HTML
report as an overlay plot.

## The math

\[
\mathrm{JS}(P\,\|\,Q) = \tfrac12\,\mathrm{KL}(P\,\|\,M) + \tfrac12\,\mathrm{KL}(Q\,\|\,M),
\qquad M = \tfrac12 (P+Q),
\qquad \mathrm{KL}(P\,\|\,M) = \sum_f P(f)\ln\frac{P(f)}{M(f)}
\]

where \(P\) and \(Q\) are the normalised mean PSDs of the real and synthetic sets.

## Reading the score

- Range **[0, ln 2 ≈ 0.693]**. 0 means identical average spectra.
- It compares **set averages**, not individual recordings. A set where half the recordings
  are too noisy and half too smooth could average out; [Spectral entropy](spectral_entropy.md)
  looks at per-recording spread instead.
- Normalising removes overall power (amplitude). Compare amplitudes separately.
- Pass the correct sampling rate (`fs`); the CLI uses the real data's rate automatically.

## Use it with ECGEN-Eval

=== "CLI"

    ```bash
    ecgen-eval eval --real real.npy --synthetic synth.npy -m psd --fs 500 --output report.html
    ```

=== "Python"

    ```python
    from ecgen_eval import load_ecg_npy, AVAILABLE_METRICS

    real = load_ecg_npy("real.npy", fs=500)
    synth = load_ecg_npy("synth.npy", fs=500)

    psd = AVAILABLE_METRICS["psd"](fs=real.fs)
    result = psd.compute(real.data, synth.data, lead_names=real.lead_names)
    print(result.score)
    mean_psd_real = result.extra["per_lead_psd_real"]   # mean PSD curves per lead
    ```

Install SciPy (`pip install scipy`) to use Welch's method. Parameters are in the
[Metric Reference](../user-guide/metric-reference.md#psd).

## Learn more

- Welch, *The use of fast Fourier transform for the estimation of power spectra*, IEEE
  Trans. Audio Electroacoust. 1967.
- Lin, *Divergence measures based on the Shannon entropy*, IEEE Trans. Inf. Theory 1991.
