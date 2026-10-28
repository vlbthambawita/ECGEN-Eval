# Dynamic Time Warping (DTW)

**Key:** `dtw` · **Family:** signal fidelity · **Better:** lower ↓ · **Per-lead:** yes

DTW asks: *how different are two waveforms once small timing differences are forgiven?*
Point-wise metrics compare sample *i* with sample *i*, so a beat that arrives 20 ms late
looks completely wrong. DTW first finds the best alignment, stretching or compressing time
locally, and then measures the remaining difference.

## Try it

The synthetic beat is drawn below the real one. Purple lines show which samples DTW matches.
On the right, the cost matrix holds the squared difference between every real sample (rows)
and every synthetic sample (columns); the orange line is the cheapest path through it.

<div class="mviz" data-viz="dtw">Interactive demo loading… (needs JavaScript)</div>

What to notice:

- **Shifted 60 ms**: the Euclidean distance is large but DTW is small, because the path
  bends to align the R peaks.
- **Shift beyond the band**: when the window is narrower than the shift, the path cannot
  reach the right alignment and DTW rises. The band limits how much warping is allowed.
- **No band**: with unlimited warping DTW becomes very forgiving, which can hide real
  morphology differences (for example a wide QRS being "squeezed" into a narrow one).

## How it works

1. Draw `n_pairs` (default 200) random (real, synthetic) pairs with a fixed seed.
2. Downsample both signals by `downsample` (default 5) to keep the cost matrix small.
3. For each lead, fill the cumulative cost matrix inside a **Sakoe–Chiba band** of
   `window × length` samples (default 10 %).
4. The DTW distance is the square root of the cheapest cumulative cost.
5. Average over pairs. The score is the mean over leads.

ECGEN-Eval uses the C implementation in `dtaidistance` when available and an equivalent
NumPy version otherwise.

## The math

\[
D(i,j) = \big(a_i - b_j\big)^2 + \min\{D(i-1,j),\ D(i,j-1),\ D(i-1,j-1)\},
\qquad |i-j| \le w
\]

\[
\mathrm{DTW}(a,b) = \sqrt{D(n,m)}
\]

with \(D(0,0)=0\) and all other boundary cells \(=\infty\). Without warping (the diagonal
path) this reduces to the Euclidean distance.

## Reading the score

- **0** means the signals match after alignment. The value is in signal units and grows with
  signal length, so compare only at the same length and sampling rate.
- Pairs are **random**, not matched: the score reflects typical real–synthetic differences
  across the sets, including genuine variety between patients. Compare with a real-vs-real
  DTW to see what is normal.
- The per-pair distances are kept in `extra["per_lead_all_distances"]`; the HTML report
  shows them as violin plots.

## Use it with ECGEN-Eval

=== "CLI"

    ```bash
    ecgen-eval eval --real real.npy --synthetic synth.npy -m dtw --output report.html
    ```

=== "Python"

    ```python
    from ecgen_eval import load_ecg_npy, AVAILABLE_METRICS

    real = load_ecg_npy("real.npy", fs=500)
    synth = load_ecg_npy("synth.npy", fs=500)

    dtw = AVAILABLE_METRICS["dtw"](n_pairs=500, downsample=5, window=0.1)
    result = dtw.compute(real.data, synth.data, lead_names=real.lead_names)
    print(result.score, result.extra["per_lead_dtw"])
    ```

Parameters are in the [Metric Reference](../user-guide/metric-reference.md#dtw).

## Learn more

- Berndt & Clifford, *Using Dynamic Time Warping to Find Patterns in Time Series*, KDD
  Workshop 1994.
- Sakoe & Chiba, *Dynamic programming algorithm optimization for spoken word recognition*,
  IEEE TASSP 1978.
